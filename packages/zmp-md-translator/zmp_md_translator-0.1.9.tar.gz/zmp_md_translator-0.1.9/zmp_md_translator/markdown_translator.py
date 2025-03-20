"""High-performance markdown translator using OpenAI's GPT models."""

import asyncio
import os
import time
from typing import List, Optional

import aiofiles
import colorlog
from openai import AsyncOpenAI

from .settings import Settings
from .types import ProgressCallback, TranslationProgress, TranslationStatus


class MarkdownTranslator:
    """High-performance markdown translator using OpenAI's GPT models."""

    MODEL_TOKEN_LIMITS = {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4o-mini": 128000,
    }

    CHARS_PER_TOKEN = 4

    def __init__(
        self,
        settings: Optional[Settings] = None,
        progress_callback: Optional[ProgressCallback] = None,
    ):
        """Initialize the translator with settings and callbacks."""
        self.settings = settings or Settings()
        self._setup_logger()
        self.client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)

        self.api_semaphore = asyncio.Semaphore(self.settings.MAX_CONCURRENT_REQUESTS)
        self.progress_callback = progress_callback
        self.completed_tasks = 0

    def _setup_logger(self):
        """Set up logging system with color formatting and timestamps."""
        logger = colorlog.getLogger("markdown_translator")
        if not logger.handlers:
            handler = colorlog.StreamHandler()
            formatter = colorlog.ColoredFormatter(
                "%(log_color)s[%(asctime)s] %(message)s",
                log_colors={
                    "DEBUG": "cyan",
                    "INFO": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "red,bg_white",
                },
                datefmt="%Y-%m-%d %H:%M:%S.%f",
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel("INFO")

    async def _report_progress(
        self,
        status: TranslationStatus,
        total: int,
        current_file: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Report translation progress through the callback function.

        Args:
            status (TranslationStatus): Current translation status
            total (int): Total number of files to process
            current_file (Optional[str]): Name of the file being processed
            message (Optional[str]): Additional status message
        """
        if self.progress_callback:
            progress = TranslationProgress(
                status=status,
                current=self.completed_tasks,
                total=total,
                current_file=current_file,
                message=message,
            )
            await self.progress_callback(progress)

    async def translate_repository(
        self,
        source_path: str,
        target_dir: str | None,
        target_languages: list[str],
        selected_solution: str | None = None,
    ) -> None:
        """
        Translate markdown files from a source directory or a single file.

        Args:
            source_path (str): Directory containing markdown files or path to a single markdown file.
            target_dir (Optional[str]): Directory to store translations. Defaults to "i18n".
            target_languages (List[str]): List of language codes to translate to.
            selected_solution (Optional[str]): Selected solution for determining target directory structure.
        """
        logger = colorlog.getLogger("markdown_translator")
        start_time = time.time()
        total_tasks = 0

        try:
            await self._report_progress(TranslationStatus.PREPARING, 0)

            # Validate source path
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source path does not exist: {source_path}")

            # Check if source is file or directory
            is_file = os.path.isfile(source_path)

            # Determine target base directory
            target_base = target_dir or "i18n"
            base_dir = os.path.abspath(target_base)

            # Use selected_solution if provided
            if not selected_solution:
                raise ValueError("selected_solution is required for translation")
            source_basename = selected_solution.lower()

            # Build language-specific target prefixes based on source_basename
            lang_target_prefixes = {}
            for lang in target_languages:
                if source_basename == "zcp":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-zcp",
                        "current",
                    )
                elif source_basename == "apim":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-apim",
                        "current",
                    )
                elif source_basename == "amdp":
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs-amdp",
                        "current",
                    )
                else:
                    prefix = os.path.join(
                        base_dir,
                        lang,
                        "docusaurus-plugin-content-docs",
                        "current",
                    )

                # Create the target directory
                os.makedirs(prefix, exist_ok=True)
                lang_target_prefixes[lang] = prefix

            # Find markdown files
            source_files = []
            source_base = os.path.dirname(source_path) if is_file else source_path
            docs_base = None

            # Find the 'docs' directory in the path
            path_parts = source_base.split(os.sep)
            for i, part in enumerate(path_parts):
                if part == "docs":
                    # Get path after 'docs' but skip the solution name (zcp, apim, amdp)
                    remaining_parts = path_parts[i + 1 :]
                    if (
                        remaining_parts
                        and remaining_parts[0].lower() == source_basename
                    ):
                        docs_base = os.sep.join(
                            remaining_parts[1:]
                        )  # Skip the solution name
                    else:
                        docs_base = os.sep.join(remaining_parts)
                    break

            if is_file:
                # For single file, use the file name as relative path
                file_name = os.path.basename(source_path)
                if docs_base:
                    rel_path = os.path.join(docs_base, file_name)
                else:
                    rel_path = file_name
                source_files.append(rel_path)
                source_path = os.path.dirname(
                    source_path
                )  # Update source_path to parent dir
            else:
                # For directory, walk through and find all markdown files
                for root, _, files in os.walk(source_path):
                    for file in files:
                        if file.endswith((".md", ".mdx")):
                            file_abs = os.path.join(root, file)
                            # Get path relative to source directory
                            rel_path = os.path.relpath(file_abs, source_path)
                            # If the first directory is the solution name, remove it
                            rel_parts = rel_path.split(os.sep)
                            if rel_parts and rel_parts[0].lower() == source_basename:
                                rel_path = os.sep.join(rel_parts[1:])
                            source_files.append(rel_path)

            total_tasks = len(source_files) * len(target_languages)
            if total_tasks == 0:
                logger.info("No markdown files found to translate")
                return True

            # Log progress
            files_count = len(source_files)
            langs_count = len(target_languages)
            logger.info(
                f"Found {files_count} file{'s' if files_count > 1 else ''} to translate "
                f"into {langs_count} language{'s' if langs_count > 1 else ''}"
            )
            logger.info(
                f"Starting translation of {files_count} file{'s' if files_count > 1 else ''} "
                f"to {langs_count} language{'s' if langs_count > 1 else ''} ({total_tasks} tasks)"
            )

            # Process translations
            await self._report_progress(TranslationStatus.TRANSLATING, total_tasks)
            all_tasks = []

            for file_path in source_files:
                content = await self._read_file(os.path.join(source_path, file_path))
                content_size = len(content)
                file_tasks = []

                for lang in target_languages:
                    target_prefix = lang_target_prefixes[lang]

                    # Get the relative path after 'docs' directory for the target
                    if docs_base:
                        # Ensure we preserve the directory structure from docs onwards
                        target_rel_path = os.path.join(docs_base, file_path)
                    else:
                        target_rel_path = file_path

                    # Join the target prefix with the source file's relative path
                    target_path = os.path.join(target_prefix, target_rel_path)

                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)

                    file_tasks.append(
                        self._translate_and_write(
                            content=content,
                            content_size=content_size,
                            target_path=target_path,
                            lang=lang,
                            total_tasks=total_tasks,
                            start_time=time.time(),
                        )
                    )
                all_tasks.append(asyncio.gather(*file_tasks))

            # Process in batches
            batch_size = self.settings.MAX_CONCURRENT_REQUESTS
            for i in range(0, len(all_tasks), batch_size):
                batch = all_tasks[i : i + batch_size]
                await asyncio.gather(*batch)

            # Log completion
            elapsed = time.time() - start_time
            if total_tasks > 0:
                per_file = elapsed / total_tasks
                logger.info(
                    "Translation completed in " f"{elapsed:.2f}s ({per_file:.2f}s/file)"
                )

            await self._report_progress(TranslationStatus.COMPLETED, total_tasks)
            logger.info("All translations completed successfully")
            return True

        except Exception as e:
            logger.error(f"Translation failed: {str(e)}")
            await self._report_progress(
                TranslationStatus.FAILED, total_tasks, message=str(e)
            )
            raise

    async def _translate_and_write(
        self,
        content: str,
        content_size: int,
        target_path: str,
        lang: str,
        total_tasks: int,
        start_time: float,
    ):
        """
        Translate content and write to target file while tracking performance.

        Handles chunking of large files, parallel translation of chunks,
        and maintains file system structure.

        Args:
            content (str): Content to translate
            content_size (int): Size of content in characters
            target_path (str): Path where translated file will be written
            lang (str): Target language code
            total_tasks (int): Total number of translation tasks
            start_time (float): Start time for performance tracking

        Raises:
            Exception: If translation or file writing fails
        """
        logger = colorlog.getLogger("markdown_translator")

        try:
            # Pre-create directory
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            async with self.api_semaphore:
                if content_size > self.settings.MAX_CHUNK_SIZE:
                    chunks = self._split_content(content, self.settings.MAX_CHUNK_SIZE)
                    # Process chunks in parallel
                    translations = await asyncio.gather(
                        *[self._translate_single_chunk(chunk, lang) for chunk in chunks]
                    )
                    translated_content = "\n".join(translations)
                else:
                    translated_content = await self._translate_single_chunk(
                        content, lang
                    )

            # Write translation
            async with aiofiles.open(target_path, "w", encoding="utf-8") as f:
                await f.write(translated_content)

            elapsed = time.time() - start_time
            rel_path = os.path.relpath(target_path)
            logger.info(f"✓ {rel_path} [{lang}] ({elapsed:.2f}s)")

            self.completed_tasks += 1
            await self._report_progress(
                TranslationStatus.TRANSLATING,
                total_tasks,
                current_file=f"{rel_path} [{lang}]",
            )

        except Exception as e:
            logger.error(f"Failed to translate to {lang}: {str(e)}")
            raise

    async def _read_file(self, path: str) -> str:
        """
        Read file content asynchronously.

        Args:
            path (str): Path to the file to read

        Returns:
            str: Content of the file

        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            return await f.read()

    def _calculate_chunk_size(self, content_size: int) -> int:
        """
        Calculate optimal chunk size based on content size and model limits.

        Adjusts chunk size dynamically based on content size to optimize
        translation performance and token usage.

        Args:
            content_size (int): Size of content in characters

        Returns:
            int: Optimal chunk size in characters
        """
        model_token_limit = self.MODEL_TOKEN_LIMITS.get(
            self.settings.OPENAI_MODEL, 4096
        )
        base_size = (model_token_limit // 2) * self.CHARS_PER_TOKEN

        # Adjust chunk size based on content size
        if content_size < 1000:
            return base_size
        elif content_size < 3000:
            return base_size * 2
        else:
            return base_size * 3  # Larger chunks for big files

    def _split_content(self, content: str, max_chunk_size: int) -> List[str]:
        """
        Split content into chunks while preserving markdown structure.

        Ensures that markdown formatting is not broken across chunks
        by splitting at appropriate boundaries.

        Args:
            content (str): Content to split
            max_chunk_size (int): Maximum size of each chunk

        Returns:
            List[str]: List of content chunks
        """
        chunks = []
        current_chunk = []
        current_size = 0

        for line in content.split("\n"):
            line_size = len(line)
            if current_size + line_size > max_chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_size = 0
            current_chunk.append(line)
            current_size += line_size + 1  # +1 for newline

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    async def _translate_single_chunk(self, chunk: str, target_language: str) -> str:
        """Translate a single chunk of text using the OpenAI API."""
        prompt = (
            f"Translate the following technical documentation to {target_language}.\n"
            "Critical requirements:\n"
            "1. NEVER TRANSLATE FRONT MATTER: Content between '---' markers at the start of the document (including id, title, sidebar_position) must remain EXACTLY as is\n"
            "2. EXACT STRUCTURE: The output must have exactly the same number of lines as the input\n"
            "3. HTML/MARKDOWN: Keep ALL tags, attributes, and markdown syntax exactly as is\n"
            "4. CODE/PATHS: Never translate code blocks, URLs, file paths, or HTML/markdown syntax\n"
            "5. WHITESPACE: Preserve all indentation, empty lines, and spacing exactly\n"
            "6. KEEP IN ENGLISH (DO NOT TRANSLATE):\n"
            "   - ALL markdown section headers (lines starting with #, ##, ###), even if they contain HTML tags\n"
            "   - ALL section IDs in curly braces (e.g., {#service-overview})\n"
            "   - ALL HTML-wrapped section headers (e.g., <b>Constraints</b>)\n"
            "   - ALL subheadings with HTML tags (e.g., <b>Supported Browsers</b>)\n"
            "   - Product names (e.g., Cloud Z CP, AWS EKS)\n"
            "   - Platform names (e.g., Kubernetes, Docker)\n"
            "   - Service names (e.g., Container Management Service)\n"
            "   - Tool names (e.g., Chrome, Gitea, Nexus)\n"
            "   - ALL version numbers and technical specifications\n"
            "   - Table headers in markdown tables\n"
            "7. TRANSLATE TO TARGET LANGUAGE:\n"
            "   - EVERY paragraph must be fully translated\n"
            "   - ALL descriptions and explanations\n"
            "   - ALL UI messages and instructions\n"
            "   - ALL list items and bullet points\n"
            "   - ALL table content (except headers)\n"
            "   - ALL sentences containing product names (translate the full sentence while keeping product names in English)\n"
            "8. FRONT MATTER EXAMPLE (DO NOT TRANSLATE):\n"
            '   - \'---\\nid: "menu-management"\\ntitle: "Menu Management"\\nsidebar_position: 4\\n---\' should remain unchanged\n'
            "9. CONSISTENCY RULES:\n"
            "   - Keep ALL section headers in English, including those with HTML tags\n"
            "   - Keep ALL subheadings in English when they use HTML tags\n"
            "   - Keep product names exactly as provided\n"
            "   - Translate EVERY sentence completely\n"
            "   - NO mixed language content allowed\n"
            "   - NO English paragraphs should remain untranslated\n"
            f"Text to translate:\n{chunk}"
        )

        response = await self.client.chat.completions.create(
            model=self.settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a markdown translator specializing in technical documentation. Follow these rules exactly:\n"
                        "1. NEVER translate front matter content between '---' markers at the beginning of files\n"
                        "2. Keep in English:\n"
                        "   - ALL section headers (lines starting with #)\n"
                        "   - Product and technology names\n"
                        "   - Tool names and specific components\n"
                        "   - Section IDs and table headers\n"
                        "3. Translate to target language:\n"
                        "   - EVERY paragraph completely\n"
                        "   - ALL descriptions and content\n"
                        "   - ALL list items and explanations\n"
                        "   - ALL sentences containing product names\n"
                        "4. Preserve exactly:\n"
                        "   - All markdown/HTML syntax\n"
                        "   - All whitespace and newlines\n"
                        "   - All formatting and tags\n"
                        "   - Front matter (content between --- markers)\n"
                        "5. Critical rules:\n"
                        "   - Never translate front matter\n"
                        "   - Never leave any paragraph in English\n"
                        "   - Never mix languages within a sentence\n"
                        "   - Translate every sentence completely\n"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,  # Use 0 for maximum consistency
        )

        return response.choices[0].message.content
