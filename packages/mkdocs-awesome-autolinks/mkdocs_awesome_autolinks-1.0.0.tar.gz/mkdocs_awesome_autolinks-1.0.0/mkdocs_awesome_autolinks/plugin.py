from collections import defaultdict
from pathlib import PurePath
import re
from typing import Optional
from mkdocs import utils
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.config.base import Config as BaseConfig
from mkdocs.config import config_options
from mkdocs.structure.files import Files, File
from mkdocs.structure.pages import Page
from mkdocs.plugins import get_plugin_logger, BasePlugin

log = get_plugin_logger(__name__)

DEFAULT_REMOVE_RE = r"^[0-9]+-"
FILE_NAME_RE = r'^(?P<path>/?.*?)(?P<file>[^/]+)\.(?P<ext>[^./]+)$'
SHORTLINK_RE = r'^(?P<link>(?![a-zA-Z][a-zA-Z0-9+.-]*://)[^?#]*)(?P<anchor>#[^/]+)?$'
IGNORE_DIRS = ['css', 'fonts', 'img', 'js', 'search', 'javascripts', 'assets/javascripts']


class AwesomeAutolinksPluginConfig(BaseConfig):
    remove_re = config_options.Type(str, default=DEFAULT_REMOVE_RE)
    warn_less = config_options.Type(bool, default=False)
    warn_on_no_use = config_options.Type(bool, default=True)
    ignore_dirs = config_options.ListOfItems(config_options.Type(str),
                                             default=IGNORE_DIRS)
    debug = config_options.Type(bool, default=False)


class AwesomeAutolinksPlugin(BasePlugin[AwesomeAutolinksPluginConfig]):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.shortlinks = defaultdict(list)
        self.remove_re = None
        self.file_name_re = re.compile(FILE_NAME_RE)
        self.shortlink_re = re.compile(SHORTLINK_RE)
        self.markdown_token_re = self.get_markdown_token_re()

    def on_pre_build(self, config: MkDocsConfig, **kwargs):
        if self.config.remove_re != DEFAULT_REMOVE_RE:
            if not self.config.remove_re:
                log.info("Removing the sorting component of file names is disabled")
                return
            log.info(f"Using configured regular expression: {self.config.remove_re}")
        try:
            self.remove_re = re.compile(self.config.remove_re)
        except re.error as e:
            log.error(f"Invalid regular expression '{self.config.remove_re}': {e.msg}")

    def set_file_dest_uri(self, f: File, dest_uri: str):
        """ Replace the destination of the given MkDocs file object """

        f.dest_uri = dest_uri
        # Delete cached properties that are based on dest_uri to force a recalculation
        if 'abs_dest_path' in f.__dict__:
            del f.__dict__['abs_dest_path']
        if 'url' in f.__dict__:
            del f.__dict__['url']

    def on_files(self, files: Files, config: MkDocsConfig, **kwargs) -> Optional[Files]:
        for f in files:
            if any(f.src_uri.startswith(dir) for dir in self.config.ignore_dirs):
                continue

            # Remove the sorting components matching the ignore regex from the path
            if self.remove_re:
                new_uri = self.delete_remove_re_from_uri(f.dest_uri)
                self.set_file_dest_uri(f, new_uri)

            # Populate the shortlinks dict with file objects

            fname_match = self.file_name_re.search(f.src_uri)
            if not fname_match:
                self.log_debug(f"No filename match on file {f.src_uri}")
                continue

            link_key_short = fname_match.group('file') + '.' + fname_match.group('ext')
            if self.remove_re:
                link_key_short = self.remove_re.sub('', link_key_short)
            self.shortlinks[link_key_short].append(f)

            path_name = fname_match.group('path') if fname_match.group('path') is not None else ""
            path_segments = PurePath(path_name).parts
            if self.remove_re:
                path_segments = [self.remove_re.sub('', path_segment) for path_segment in path_segments]
            for i in range(len(path_segments)):
                segment_path = '/'.join(path_segments[i:])
                link_key_long = f"{segment_path}/{link_key_short}"
                self.shortlinks[link_key_long].append(f)

        if self.config.debug:
            for link_key, link_files in sorted(self.shortlinks.items()):
                links_str = ', '.join([f"'{lf.src_uri}'" for lf in link_files])
                self.log_debug(f"Added short link '{link_key}' for page{'s' if len(link_files) > 1 else ''} {links_str}")

        return

    def get_markdown_token_re(self) -> re.Pattern:
        token_specification = [
            ('CODE_BLOCK', r'(?<!\\)(?P<blk_ticks>`{3,})(?s:.+?)(?P=blk_ticks)'),
            ('INLINE_CODE', r'(?<!\\)(?P<in_ticks>`{1,2})(?:.|\n(?!\n))+?(?<!`)(?P=in_ticks)(?!`)'),
            ('ESCAPED_TICK', r'\\`'),
            ('DIRECT_LINK', r'\[(?P<dl_txt>[^]]*)\]\((?P<dl_ref>[^)]*)\)'),
            ('INDIRECT_LINK', r'\[(?P<il_txt>[^]]+)\]:\s+(?P<il_ref>\S+)'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)

        return re.compile(tok_regex)

    def on_page_markdown(self, markdown: str, page: Page, config: MkDocsConfig, files: Files, **kwargs) -> Optional[str]:
        self.log_debug(f"START processing markdown of page {page.file.src_uri}")
        start_pos = 0
        end_pos = len(markdown) - 1
        segments = []
        while start_pos <= end_pos:
            m = self.markdown_token_re.search(markdown, start_pos)
            if not m:
                segments.append(markdown[start_pos:])
                start_pos = end_pos + 1
                continue
            kind = m.lastgroup
            segments.append(markdown[start_pos:m.start()])
            start_pos = m.start()

            if kind in ['CODE_BLOCK', 'INLINE_CODE', 'ESCAPED_TICK']:
                segments.append(markdown[start_pos:m.end()])
            elif kind == 'DIRECT_LINK':
                self.log_debug(f"Markdown token {kind} with value {m.group()}")
                new_link = self.replace_link(m.group('dl_ref'), page.file)
                segments.append(f"[{m.group('dl_txt')}]({new_link})")
            elif kind == 'INDIRECT_LINK':
                self.log_debug(f"Markdown token {kind} with value {m.group()}")
                new_link = self.replace_link(m.group('il_ref'), page.file)
                segments.append(f"[{m.group('il_txt')}]: {new_link}")
            else:
                log.warning(f'Missing code for handling token {kind} while parsing markdown of {page.file.src_uri}')
                segments.append(markdown[start_pos:m.end()])

            start_pos = m.end()

        self.log_debug(f"END processing markdown of page '{page.file.src_uri}'")

        return ''.join(segments)

    def replace_link(self, link: str, page_file: File) -> str:
        """ Replace the link with the corresponding shortlink if it exists """

        m = self.shortlink_re.search(link)
        if not m:
            return link

        if not m.group('link'):
            # Only anchor link
            return link
    
        new_link = self.get_link_from_shortlinks(m.group('link'), page_file)
        if not new_link:
            if self.config.warn_on_no_use:
                log.warning(f"Awesome autolink functionality not used in link '{m.group('link')}' on page '{page_file.src_uri}'")
            return link

        if m.group('anchor'):
            new_link += m.group('anchor')

        if self.config.debug and link != new_link:
            self.log_debug(f"Replaced '{link}' with '{new_link}' on page '{page_file.src_uri}'")

        return new_link

    def get_link_from_shortlinks(self, link: str, page_file: File) -> str:
        """ 
        Get the link from the shortlinks dict. 
        If multiple links are available, try to find one in the same or a lower level directory of the page. 
        """

        dst_files = self.shortlinks.get(link)
        if not dst_files:
            return None

        if len(dst_files) == 1:
            return utils.get_relative_url(dst_files[0].src_uri, page_file.src_uri)

        # Multiple destinations available, see if we can find a single one at the same or a lower level directory of the page
        found_in_branch = 0
        new_link = None
        for dst_file in dst_files:
            rel_link = utils.get_relative_url(dst_file.src_uri, page_file.src_uri)
            if rel_link.startswith('../'):
                if found_in_branch == 0 and not new_link:
                    new_link = rel_link
            else:
                found_in_branch += 1
                if found_in_branch == 1:
                    new_link = rel_link

        if found_in_branch != 1:
            # Either multiple links outside the directory branch of the page or multiple links inside the directory branch of the page or both
            log.warning(f"Multiple destinations available for link '{link}' on page '{page_file.src_uri}")
        elif not self.config.warn_less:
            # There is a single link in the same directory branch of the page but we are informing about it anyway
            log.warning(f"Multiple destinations available for link '{link}' on page '{page_file.src_uri}` but found one in the same directory branch of the page")

        return new_link

    def delete_remove_re_from_uri(self, uri: str) -> str:
        """ Remove all the sorting component matching the ignore regex from the path """

        components = []

        for dir in PurePath(uri).parts:
            components.append(self.remove_re.sub('', dir))

        return '/'.join(components)

    def log_debug(self, message: str):
        """ Log a debug message if debug is enabled """

        if self.config.debug:
            log.info(f"DEBUG - {message}")
