from kubespawner.slugs import safe_slug
from kubespawner.spawner import KubeSpawner as KubeSpawner_
from traitlets import Unicode


class KubeSpawner(KubeSpawner_):
    public_url_pattern = Unicode(
        None,
        allow_none=False,
        config=True,
        help="The URL pattern for the public URL",
    )

    def start(self):
        self.log.info("Detecting workspace...")
        if "workspace" not in self.user_options:
            self.log.info(
                "No workspace detected in user options. Aborting notebook launch."
            )
            raise NoWorkspaceSet("No workspace detected in user options.")
        self.workspace = self.user_options["workspace"]
        self.log.info(f"Workspace detected: {self.workspace}")
        if self.public_url_pattern:
            self.public_url = self._expand_user_properties(self.public_url_pattern)
        return super().start()

    def get_state(self):
        """
        Add workspace to the state
        """
        state = super().get_state()
        state["workspace"] = self.workspace
        return state

    def get_env(self):
        """
        Add workspace to the environment
        """
        env = super().get_env()
        env["WORKSPACE"] = self.workspace
        return env

    def load_state(self, state):
        """
        Load workspace from state
        """
        super().load_state(state)
        self.workspace = state.get("workspace", None)

    def _expand_user_properties(self, template, slug_scheme=None):
        """
        Expand user properties in template strings
        """
        safe_username = safe_slug(self.user.name)
        safe_workspace = safe_slug(self.workspace)
        servername = f"{safe_username}--{safe_workspace}"
        ns = dict(
            username=safe_slug(self.user.name),
            workspace=safe_slug(self.workspace),
            servername=servername,
            user_server=servername,
        )
        for attr_name in ("pod_name", "pvc_name", "namespace", "workspace"):
            ns[attr_name] = getattr(self, attr_name, f"{attr_name}_unavailable!")
        return template.format(**ns)


class NoWorkspaceSet(Exception):
    pass
