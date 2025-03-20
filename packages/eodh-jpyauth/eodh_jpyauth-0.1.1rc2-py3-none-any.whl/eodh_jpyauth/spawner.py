from kubespawner.spawner import KubeSpawner
from traitlets import Unicode


class EODHSpawner(KubeSpawner):
    workspace = Unicode(
        None,
        allow_none=False,
        config=True,
        help="The workspace of the notebook",
    )

    def _expand_user_properties(self, template, slug_scheme=None):
        """
        Expand user properties in template strings
        """
        ns = dict(
            username=self.user.name,
            workspace=self.workspace,
        )
        for attr_name in ("pod_name", "pvc_name", "namespace"):
            ns[attr_name] = getattr(self, attr_name, f"{attr_name}_unavailable!")
        return template.format(**ns)
