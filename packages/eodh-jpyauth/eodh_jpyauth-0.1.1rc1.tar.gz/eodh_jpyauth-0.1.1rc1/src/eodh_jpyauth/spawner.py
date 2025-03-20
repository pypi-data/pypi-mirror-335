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
        return template.format(
            username=self.user.name,
            workspace=self.workspace,
        )
