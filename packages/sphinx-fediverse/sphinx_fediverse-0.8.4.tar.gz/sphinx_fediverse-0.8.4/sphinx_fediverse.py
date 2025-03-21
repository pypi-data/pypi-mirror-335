from __future__ import annotations

from json import dump, load
from os import getenv
from pathlib import Path
from shutil import copyfile
from typing import TYPE_CHECKING, cast

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:  # cov: ignore
    from typing import Any, Dict, List, Set, Union

    from sphinx.application import Sphinx
    from sphinx.config import Config

package_json_path = Path(__file__).parent / "package.json"
if not package_json_path.exists():
    copyfile(Path(__file__).parent.parent / "jssrc" / "package.json", package_json_path)
with package_json_path.open('r') as f:
    version = load(f)['version']

__version__ = tuple(int(x) for x in version.split("."))

registered_docs: Set[str] = set()


class FediverseCommentDirective(SphinxDirective):
    has_content = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.post_id = None

    def process_post(self, post_url: str, title: str) -> str:
        """Post a new comment on Mastodon and return the post ID."""
        if not self.config.enable_post_creation:
            if not self.config.raise_error_if_no_post:
                return ''
            elif input('Would you like to create the post yourself, and provide the ID? (y/N) ').lower()[0] == 'y':
                return input("Enter the ID and NOTHING ELSE: ")
            else:
                raise RuntimeError(f"Post creation is disabled. Cannot create a post for {post_url}")
        elif self.env.config.fedi_flavor == 'mastodon':
            return self.process_mastodon(post_url, title)
        elif self.env.config.fedi_flavor == 'misskey':
            return self.process_misskey(post_url, title)
        raise EnvironmentError("Unknown fediverse flavor selected")

    def process_mastodon(self, post_url: str, title: str) -> str:
        from mastodon import Mastodon

        if not all((
            getenv('MASTODON_CLIENT_ID'),
            getenv('MASTODON_CLIENT_SECRET'),
            getenv('MASTODON_ACCESS_TOKEN')
        )):
            raise EnvironmentError("Must provide all 3 mastodon access tokens")
        else:
            api = Mastodon(
                api_base_url=self.env.config.fedi_instance,
                client_id=getenv('MASTODON_CLIENT_ID'),
                client_secret=getenv('MASTODON_CLIENT_SECRET'),
                access_token=getenv('MASTODON_ACCESS_TOKEN'),
                user_agent=f'Sphinx-Fediverse v{".".join(str(x) for x in __version__)}',
            )
            message = f"Discussion post for {title}\n\n{self.env.config.html_baseurl}"
            message.rstrip('/')
            message += '/'
            message += post_url
            post = api.status_post(
                status=message, visibility='public', language='en',
            )
            return cast(str, post.id)

    def process_misskey(self, post_url: str, title: str) -> str:
        from misskey import Misskey

        if not getenv('MISSKEY_ACCESS_TOKEN'):
            raise EnvironmentError("Must provide misskey access token")
        else:
            api = Misskey(
                self.env.config.fedi_instance,
                i=getenv('MISSKEY_ACCESS_TOKEN'),
                # user_agent=f'Sphinx-Fediverse v{'.'.join(str(x) for x in __version__)}',
            )
            escaped_url = post_url.replace(')', r'\)')
            url = f"{self.env.config.html_baseurl.rstrip('/')}/{escaped_url}"
            message = f"Discussion post for [{title}]({url})"
            post = api.notes_create(
                text=message, visibility='public',
            )
            return cast(str, post['createdNote']['id'])

    def create_post_if_needed(self, post_url: str) -> str:
        """Check if a post exists for this URL. If not, create one."""
        # Read the mapping file
        mapping_file_path = Path(self.config.comments_mapping_file)
        if not mapping_file_path.exists():
            # File doesn't exist, create an empty mapping
            mapping: Dict[str, str] = {}
        else:
            with open(mapping_file_path, "r") as f:
                mapping = load(f)

        # Check if this URL already has a post ID
        if post_url in mapping:
            return mapping[post_url]

        # If not, create the post
        for node in self.state.document.traverse(nodes.title):
            title = node.astext()
            break  # accept the first title seen

        post_id = self.process_post(post_url, title)
        if post_id:
            mapping[post_url] = post_id
            # Save the updated mapping back to the file
            with open(mapping_file_path, "w") as f:
                dump(mapping, f, indent=2)

        return post_id

    def run(self) -> List[nodes.raw]:
        """Main method to execute the directive."""
        # Fetch base URL from conf.py (html_baseurl)
        if self.env.app.builder.name != 'html':
            raise EnvironmentError("Cannot function outside of html build")

        base_url = self.config.html_baseurl
        if not base_url:
            raise ValueError("html_baseurl must be set in conf.py for Fediverse comments to work.")

        # Get the final output document URL using base_url + docname
        docname = self.env.docname
        if docname in registered_docs:
            raise RuntimeError("Cannot include two comments sections in one document")
        registered_docs.add(docname)

        # Handle special case for index.html and use configurable URL format
        if docname == "index":
            if self.config.replace_index_with_slash:
                post_url = "/"  # Replace index.html with just a slash
            else:
                post_url = "index.html"  # Keep the index.html
        else:
            post_url = docname + ".html"  # Always use .html extension

        # Create or retrieve the post ID
        post_id = self.create_post_if_needed(post_url)

        if post_id is None:
            return []

        # Create the DOM element to store the post ID
        post_id_node = nodes.raw('', f"""
            <div style="display:none;">
                <span id="fedi-post-id">{post_id}</span>
                <span id="fedi-instance">{self.env.config.fedi_instance}</span>
                <span id="fedi-flavor">{self.env.config.fedi_flavor}</span>
            </div>
            <h2>
                Comments
                <span class="comments-info">
                    <img class="fediIcon" src="{self.env.config.html_baseurl}/_static/boost.svg" alt="Boosts">
                    <span id="global-reblogs"></span>,
                    <img class="fediIcon" src="{self.env.config.html_baseurl}/_static/like.svg" alt="Likes">
                    <span id="global-likes"></span>
                </span>
            </h2>
            <div id="comments-section"></div>
            <script>
            document.addEventListener("DOMContentLoaded", function () {{
                const postIdElement = document.getElementById('fedi-post-id');
                const fediInstanceElement = document.getElementById('fedi-instance');
                if (postIdElement && fediInstanceElement) {{
                    const postId = postIdElement.textContent || postIdElement.innerText;
                    const fediInstance = fediInstanceElement.textContent || fediInstanceElement.innerText;
                    if (postId) {{
                        setImageLink(
                            "{self.env.config.html_baseurl}/_static/boost.svg"
                        )
                        // Trigger the comment-fetching logic on page load
                        fetchComments(fediInstance, postId, 5); // Adjust depth as needed
                    }}
                }}
            }});
          </script>
        """, format='html')

        # Add the post ID element to the document
        self.add_name(post_id_node)
        return [post_id_node]


def on_builder_inited(app: Sphinx) -> None:
    if app.builder.name != 'html':
        return
    for file_path in Path(__file__).parent.joinpath('_static').iterdir():
        if file_path.is_file():
            out_path = Path(app.builder.outdir, f'_static/{file_path.name}')
            out_path.parent.mkdir(exist_ok=True, parents=True)
            copyfile(file_path, out_path)
    if Path(app.config.comments_mapping_file).exists():
        copyfile(
            app.config.comments_mapping_file,
            Path(app.builder.outdir, '_static', app.config.comments_mapping_file)
        )


def on_config_inited(app: Sphinx, config: Config) -> None:
    app.config.html_js_files.append(f'fedi_script_{app.config.fedi_flavor}.min.js')
    if app.config.fedi_flavor == 'misskey':
        app.config.html_js_files.append('marked.min.js')


def setup(app: Sphinx) -> Dict[str, Union[str, bool]]:
    # Register custom configuration options
    app.add_config_value('fedi_flavor', '', 'env')
    app.add_config_value('fedi_username', '', 'env')
    app.add_config_value('fedi_instance', '', 'env')
    app.add_config_value('enable_post_creation', True, 'env')
    app.add_config_value('comments_mapping_file', 'comments_mapping.json', 'env')
    app.add_config_value('replace_index_with_slash', True, 'env')
    app.add_config_value('raise_error_if_no_post', True, 'env')

    app.add_directive('fedi-comments', FediverseCommentDirective)
    app.connect('builder-inited', on_builder_inited)
    app.connect('config-inited', on_config_inited)

    app.config.html_js_files.append('purify.min.js')
    app.config.html_js_files.append('fedi_script.min.js')
    app.config.html_css_files.append('fedi_layout.css')

    return {
        'version': '.'.join(str(x) for x in __version__),
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
