"""
Make the update of default branch, visibility, merge method and merge restriction.
"""

# Standard Library
from textwrap import indent
from typing import List
from typing import Optional

# Third Party Libraries
import click

from boltons.cacheutils import cachedproperty
from gitlab.exceptions import GitlabGetError
from gitlab.v4.objects import Project

# Gitlab-Project-Configurator Modules
from gpc.change_setting import ChangeSetting
from gpc.executors.base_setting_executor import BaseSettingExecutor
from gpc.executors.base_setting_executor import ClusterUpdator
from gpc.executors.base_setting_executor import LocalUpdator
from gpc.executors.base_setting_executor import PermissionsUpdator
from gpc.executors.base_setting_executor import VisibilityUpdator
from gpc.helpers.exceptions import GpcError
from gpc.helpers.gitlab_helper import INV_SQUASH_OPTIONS
from gpc.helpers.gitlab_helper import MERGE_METHODS
from gpc.helpers.gitlab_helper import SQUASH_OPTIONS
from gpc.helpers.graphql_helper import GraphqlSingleton
from gpc.helpers.types import ProjectRule
from gpc.parameters import GpcParameters
from gpc.parameters import RunMode


class ProjectSettingExecutor(BaseSettingExecutor):
    applicable_to = ["project"]
    sections = ["default_branch", "permissions", "mergerequests"]
    project_properties = [
        "default_branch",
        "description",
        "topics",
        "ci_config_path",
        "ci_git_shallow_clone",
        "auto_cancel_pending_pipelines",
        "build_coverage_regex",
        "squash_commit_template",
        "merge_suggestion_message",
        "merge_commit_template",
        "merge_requests_template",
    ]

    @cachedproperty
    def updators(self):
        return ProjectUpdatorFactory.init_updators(
            self.item, self.rule, self.show_diff_only, self.gpc_params
        )

    @cachedproperty
    def default_branch_updator(self):
        for updator in self.updators:
            if isinstance(updator, DefaultBranchUpdator):
                return updator
        return None

    def _apply(self):
        if not self.default_branch_updator.success:
            click.secho(
                "ERROR: The default branch can not be updated because an error "
                f"occurred previously: {self.default_branch_updator.error}",
                fg="red",
            )
            self.success = False
        super()._apply()


class ProjectUpdatorFactory:
    @staticmethod
    def init_updators(
        project: Project, rule: ProjectRule, show_diff_only: bool, gpc_params: GpcParameters
    ):
        updators = [
            DefaultBranchUpdator(project, rule, show_diff_only),
            DescriptionUpdator(project, rule, show_diff_only),
            TopicsUpdator(project, rule, show_diff_only),
            CiConfigPathUpdator(project, rule, show_diff_only),
            AutoCancelPendingPipelinesUpdator(project, rule, show_diff_only),
            MergeCommitTemplateUpdator(project, rule, show_diff_only),
            MergeSuggestionMessageUpdator(project, rule, show_diff_only),
            SquashCommitTemplateUpdator(project, rule, show_diff_only),
            IssuesTemplateUpdator(project, rule, show_diff_only),
            BuildCoverageRegexUpdator(project, rule, show_diff_only),
            CIGitShallowCloneUpdator(project, rule, show_diff_only),
            ClusterUpdator(
                "artifacts",
                [
                    KeepLatestArtifactUpdator,
                ],
                project,
                rule,
                show_diff_only,
            ),
            ClusterUpdator(
                "permissions",
                [
                    VisibilityUpdator,
                    RequestAccessUpdator,
                    WikiEnabledUpdator,
                    IssuesEnabledUpdator,
                    SnippetsEnabledUpdator,
                    LfsEnabledUpdator,
                    ContainerRegistryEnabledUpdator,
                    JobsEnabledUpdator,
                    MergeRequestsEnabledUpdator,
                    PackagesEnabled,
                    ReleasesAccessLevelUpdator,
                    InfrastructureAccessLevelUpdator,
                    FeatureFlagsAccessLevelUpdator,
                    EnvironmentsAccessLevelUpdator,
                    MonitorAccessLevelUpdator,
                    PagesAccessLevelUpdator,
                    AnalyticsAccessLevelUpdator,
                    ForkingAccessLevelUpdator,
                    SecurityAndComplianceAccessLevelUpdator,
                    IssuesAccessLevelUpdator,
                    RepositoryAccessLevelUpdator,
                    MergeRequestsAccessLevelUpdator,
                    WikiAccessLevelUpdator,
                    BuildsAccessLevelUpdator,
                    SnippetsAccessLevelUpdator,
                    ContainerRegistryAccessLevelUpdator,
                    ModelExperimentsAccessLevelUpdator,
                    ModelRegistryAccessLevelUpdator,
                    RequirementsAccessLevelUpdator,
                ],
                project,
                rule,
                show_diff_only,
            ),
            ClusterUpdator(
                "mergerequests",
                [
                    MergeDiscussionResolvedUpdator,
                    MergePipelineSuccessUpdator,
                    ResolveOutdatedDiscussionsUpdator,
                    PrintMRLinkUpdator,
                    RemoveSourceBranchUpdator,
                    MergeMethodUpdator,
                    SquashOptionUpdator,
                    ResultPipelineUpdator,
                    MergeTrainUpdator,
                    MergeRequestsTemplateUpdator,
                    TokenAccessUpdator,
                    SkippedPipelineIsSucceedPipeline,
                ],
                project,
                rule,
                show_diff_only,
            ),
            ClusterUpdator(
                "access_token",
                [Allow_Token_Ci_Updator, AllowList],
                project,
                rule,
                show_diff_only,
                params=gpc_params,
            ),
        ]
        return updators


class DefaultBranchUpdator(LocalUpdator):
    def update(self):
        if "default_branch" in self.rule and self.rule.default_branch:
            force_create_default_branch = (
                "force_create_default_branch" in self.rule and self.rule.force_create_default_branch
            )
            ignore_inexistant_branch = (
                "ignore_inexistant_branch" in self.rule and self.rule.ignore_inexistant_branch
            )
            if ignore_inexistant_branch:
                click.secho(
                    "WARNING: ignore_inexistant_branch is activated. "
                    "This means that:\n"
                    f"- If the desired default branch '{self.rule.default_branch}'"
                    "does not exist, it will be ignored.",
                    fg="yellow",
                )
                if not force_create_default_branch:
                    branch_exists = self.exist_branch(self.rule.default_branch)
                    if not branch_exists:
                        return None
            branch_treatment = (
                self.create_default_branch if force_create_default_branch else self.exist_branch
            )
            if branch_treatment(self.rule.default_branch):
                change_setting = ChangeSetting(
                    property_name="default_branch",
                    before=self.item.default_branch,
                    after=self.rule.default_branch,
                    show_diff_only=self.show_diff_only,
                )
                self.item.default_branch = self.rule.default_branch
            else:
                change_setting = ChangeSetting(
                    property_name="default_branch",
                    before=self.item.default_branch,
                    after=f"{self.rule.default_branch} (does not exist)",
                    show_diff_only=self.show_diff_only,
                )
                change_setting.action = "error"
            return change_setting
        return None

    def create_default_branch(self, branch_name):
        try:
            self.item.branches.get(branch_name, retry_transient_errors=True)
            return True
        except GitlabGetError as exc:
            if exc.response_code == 404:
                # if the branch does not exist we create it
                self.item.branches.create(
                    {"branch": branch_name, "ref": self.item.default_branch},
                    retry_transient_errors=True,
                )
                return True

            raise

    def exist_branch(self, branch_name):
        try:
            self.item.branches.get(branch_name, retry_transient_errors=True)
            return True
        except GitlabGetError as exc:
            if exc.response_code in (404, 500):
                # Gitlab.org may return error 500 for projects that does not have
                # any branch
                self.success = False
                self.error = (
                    f"The branch {branch_name} does not exist for"
                    f" the project {self.item.path_with_namespace}."
                )
                click.secho(
                    f"/!\\ {self.error} The default branch will not be updated."
                    "You may try with force_create_default_branch option to force its creation.",
                    fg="yellow",
                )
                return False
            raise


class ArtifactsUpdator(LocalUpdator):
    artifact_param_name = None  # type: str

    def update(self):
        if "artifacts" in self.rule and self.artifact_param_name in self.rule.artifacts:
            self.filter_value(getattr(self.rule.artifacts, self.artifact_param_name))
            change_setting = ChangeSetting(
                property_name=self.artifact_param_name,
                before=getattr(self.item, self.artifact_param_name),
                after=getattr(self.rule.artifacts, self.artifact_param_name),
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            setattr(
                self.item,
                self.artifact_param_name,
                getattr(self.rule.artifacts, self.artifact_param_name),
            )
            return change_setting
        return None

    def filter_value(self, _value):
        pass


class KeepLatestArtifactUpdator(ArtifactsUpdator):
    artifact_param_name = "keep_latest_artifact"


class DescriptionUpdator(LocalUpdator):
    def update(self):
        if "description" in self.rule:
            change_setting = ChangeSetting(
                property_name="description",
                before=self.item.description,
                after=self.rule.description,
                show_diff_only=self.show_diff_only,
            )
            self.item.description = self.rule.description
            return change_setting
        return None


class TopicsUpdator(LocalUpdator):
    def update(self):
        if "topics" in self.rule and isinstance(self.rule.topics, list):
            if self.rule.get("keep_existing_topics", False):
                for topic in self.item.topics:
                    if topic not in self.rule.topics:
                        self.rule.topics.append(topic)
            change_setting = ChangeSetting(
                property_name="topics",
                before=self.item.topics,
                after=self.rule.topics,
                show_diff_only=self.show_diff_only,
            )
            self.item.topics = self.rule.topics
            return change_setting
        return None


class CiConfigPathUpdator(LocalUpdator):
    def update(self):
        if "ci_config_path" in self.rule:
            change_setting = ChangeSetting(
                property_name="ci_config_path",
                before=self.item.ci_config_path,
                after=self.rule.ci_config_path,
                show_diff_only=self.show_diff_only,
            )
            self.item.ci_config_path = self.rule.ci_config_path
            return change_setting
        return None


class AutoCancelPendingPipelinesUpdator(LocalUpdator):
    def update(self):
        if "auto_cancel_pending_pipelines" in self.rule:
            change_setting = ChangeSetting(
                property_name="auto_cancel_pending_pipelines",
                before=self.item.auto_cancel_pending_pipelines,
                after=self.rule.auto_cancel_pending_pipelines,
                show_diff_only=self.show_diff_only,
            )
            self.item.auto_cancel_pending_pipelines = self.rule.auto_cancel_pending_pipelines
            return change_setting
        return None


class MergeCommitTemplateUpdator(LocalUpdator):
    def update(self):
        if "merge_commit_template" in self.rule:
            change_setting = ChangeSetting(
                property_name="merge_commit_template",
                before=self.item.merge_commit_template,
                after=self.rule.merge_commit_template,
                show_diff_only=self.show_diff_only,
            )
            self.item.merge_commit_template = self.rule.merge_commit_template
            return change_setting
        return None


class MergeSuggestionMessageUpdator(LocalUpdator):
    def update(self):
        if "merge_suggestion_message" in self.rule:
            change_setting = ChangeSetting(
                property_name="merge_suggestion_message",
                before=self.item.suggestion_commit_message,
                after=self.rule.merge_suggestion_message,
                show_diff_only=self.show_diff_only,
            )
            self.item.suggestion_commit_message = self.rule.merge_suggestion_message
            return change_setting
        return None


class SquashCommitTemplateUpdator(LocalUpdator):
    def update(self):
        if "squash_commit_template" in self.rule:
            change_setting = ChangeSetting(
                property_name="squash_commit_template",
                before=self.item.squash_commit_template,
                after=self.rule.squash_commit_template,
                show_diff_only=self.show_diff_only,
            )
            self.item.squash_commit_template = self.rule.squash_commit_template
            return change_setting
        return None


class IssuesTemplateUpdator(LocalUpdator):
    def update(self):
        if "issues_template" in self.rule:
            change_setting = ChangeSetting(
                property_name="issues_template",
                before=self.item.issues_template,
                after=self.rule.issues_template,
                show_diff_only=self.show_diff_only,
            )
            self.item.issues_template = self.rule.issues_template
            return change_setting
        return None


class MergeRequestsTemplateUpdator(LocalUpdator):
    def update(self):
        if "mergerequests" in self.rule and "default_template" in self.rule.mergerequests:
            change_setting = ChangeSetting(
                property_name="merge_requests_template",
                before=self.item.merge_requests_template,
                after=self.rule.mergerequests.default_template,
                show_diff_only=self.show_diff_only,
            )
            self.item.merge_requests_template = self.rule.mergerequests.default_template
            return change_setting
        return None


class BuildCoverageRegexUpdator(LocalUpdator):
    def update(self):
        if "build_coverage_regex" in self.rule:
            self.error = "build_coverage_regex deprecated in Gitlab 15.0"


class CIGitShallowCloneUpdator(LocalUpdator):
    def update(self):
        if "ci_git_shallow_clone" in self.rule:
            p_ci_git_shallow_clone = self.item.ci_default_git_depth
            # 0 or None are the same value for gitlab
            if not self.item.ci_default_git_depth:
                p_ci_git_shallow_clone = None
            r_ci_git_shallow_clone = self.rule.ci_git_shallow_clone
            # 0 or None are the same value for gitlab
            if not self.rule.ci_git_shallow_clone:
                r_ci_git_shallow_clone = None
            change_setting = ChangeSetting(
                property_name="ci_git_shallow_clone",
                before=p_ci_git_shallow_clone,
                after=r_ci_git_shallow_clone,
                show_diff_only=self.show_diff_only,
            )
            self.item.ci_default_git_depth = self.rule.ci_git_shallow_clone
            return change_setting
        return None


class RequestAccessUpdator(PermissionsUpdator):
    permission_rule_name = "request_access_enabled"


class WikiEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "wiki_enabled"


class IssuesEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "issues_enabled"


class SnippetsEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "snippets_enabled"


class LfsEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "lfs_enabled"


class ContainerRegistryEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "container_registry_enabled"


class ReleasesAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "releases_access_level"


class InfrastructureAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "infrastructure_access_level"


class FeatureFlagsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "feature_flags_access_level"


class EnvironmentsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "environments_access_level"


class MonitorAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "monitor_access_level"


class PagesAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "pages_access_level"


class AnalyticsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "analytics_access_level"


class ForkingAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "forking_access_level"


class SecurityAndComplianceAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "security_and_compliance_access_level"


class IssuesAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "issues_access_level"


class RepositoryAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "repository_access_level"


class MergeRequestsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "merge_requests_access_level"


class WikiAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "wiki_access_level"


class BuildsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "builds_access_level"


class SnippetsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "snippets_access_level"


class ContainerRegistryAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "container_registry_access_level"


class ModelExperimentsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "model_experiments_access_level"


class ModelRegistryAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "model_registry_access_level"


class RequirementsAccessLevelUpdator(PermissionsUpdator):
    permission_rule_name = "requirements_access_levell"


class JobsEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "jobs_enabled"


class MergeRequestsEnabledUpdator(PermissionsUpdator):
    permission_rule_name = "merge_requests_enabled"


class PackagesEnabled(PermissionsUpdator):
    permission_rule_name = "packages_enabled"


class MergeDiscussionResolvedUpdator(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "only_allow_merge_if_all_discussions_are_resolved" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="only_allow_merge_if_all_discussions_are_resolved",
                before=self.item.only_allow_merge_if_all_discussions_are_resolved,
                after=mr_config.only_allow_merge_if_all_discussions_are_resolved,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.only_allow_merge_if_all_discussions_are_resolved = (
                mr_config.only_allow_merge_if_all_discussions_are_resolved
            )
            return change_setting
        return None


class SkippedPipelineIsSucceedPipeline(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "allow_merge_on_skipped_pipeline" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="allow_merge_on_skipped_pipeline",
                before=self.item.allow_merge_on_skipped_pipeline,
                after=mr_config.allow_merge_on_skipped_pipeline,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.allow_merge_on_skipped_pipeline = mr_config.allow_merge_on_skipped_pipeline
            return change_setting
        return None


class MergePipelineSuccessUpdator(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "only_allow_merge_if_pipeline_succeeds" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="only_allow_merge_if_pipeline_succeeds",
                before=self.item.only_allow_merge_if_pipeline_succeeds,
                after=mr_config.only_allow_merge_if_pipeline_succeeds,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.only_allow_merge_if_pipeline_succeeds = (
                mr_config.only_allow_merge_if_pipeline_succeeds
            )
            return change_setting
        return None


class ResolveOutdatedDiscussionsUpdator(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "resolve_outdated_diff_discussions" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="resolve_outdated_diff_discussions",
                before=self.item.resolve_outdated_diff_discussions,
                after=mr_config.resolve_outdated_diff_discussions,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.resolve_outdated_diff_discussions = (
                mr_config.resolve_outdated_diff_discussions
            )
            return change_setting
        return None


class PrintMRLinkUpdator(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "printing_merge_request_link_enabled" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="printing_merge_request_link_enabled",
                before=self.item.printing_merge_request_link_enabled,
                after=mr_config.printing_merge_request_link_enabled,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.printing_merge_request_link_enabled = (
                mr_config.printing_merge_request_link_enabled
            )
            return change_setting
        return None


class RemoveSourceBranchUpdator(LocalUpdator):
    def update(self):
        if (
            "mergerequests" in self.rule
            and "remove_source_branch_after_merge" in self.rule.mergerequests
        ):
            mr_config = self.rule.mergerequests
            change_setting = ChangeSetting(
                property_name="remove_source_branch_after_merge",
                before=self.item.remove_source_branch_after_merge,
                after=mr_config.remove_source_branch_after_merge,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.remove_source_branch_after_merge = mr_config.remove_source_branch_after_merge
            return change_setting
        return None


class MergeMethodUpdator(LocalUpdator):
    def update(self):
        if "mergerequests" in self.rule and "merge_method" in self.rule.mergerequests:
            merge_method = self.rule.mergerequests.merge_method
            if merge_method not in MERGE_METHODS:
                raise ValueError(
                    f"Invalid merge method : '{merge_method}', expected : {MERGE_METHODS}"
                )
            change_setting = ChangeSetting(
                property_name="merge_method",
                before=self.item.merge_method,
                after=merge_method,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.merge_method = merge_method
            return change_setting
        return None


class SquashOptionUpdator(LocalUpdator):
    def update(self):
        if "mergerequests" in self.rule and "squash_option" in self.rule.mergerequests:
            squash_option = self.rule.mergerequests.squash_option
            if squash_option not in SQUASH_OPTIONS:
                raise ValueError(
                    f"Invalid squash option : '{squash_option}', expected : {SQUASH_OPTIONS.keys()}"
                )
            change_setting = ChangeSetting(
                property_name="squash_option",
                before=INV_SQUASH_OPTIONS[self.item.squash_option],
                after=squash_option,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.squash_option = SQUASH_OPTIONS[squash_option]
            return change_setting
        return None


class ResultPipelineUpdator(LocalUpdator):
    def update(self):
        if "mergerequests" in self.rule and "merge_pipelines_enabled" in self.rule.mergerequests:
            merge_pipelines_enabled = self.rule.mergerequests.merge_pipelines_enabled
            change_setting = ChangeSetting(
                property_name="merge_pipelines_enabled",
                before=self.item.merge_pipelines_enabled,
                after=merge_pipelines_enabled,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.merge_pipelines_enabled = merge_pipelines_enabled
            return change_setting

        return None


class MergeTrainUpdator(LocalUpdator):
    def update(self):
        if "mergerequests" in self.rule and "merge_trains_enabled" in self.rule.mergerequests:
            merge_trains_enabled = self.rule.mergerequests.merge_trains_enabled
            change_setting = ChangeSetting(
                property_name="merge_trains_enabled",
                before=self.item.merge_trains_enabled,
                after=merge_trains_enabled,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            self.item.merge_trains_enabled = merge_trains_enabled
            return change_setting
        return None


class TokenAccessUpdator(LocalUpdator):
    property_name = None  # type: str
    api_name = None  # type: str
    update_template = indent(
        """ mutation {{
                projectCiCdSettingsUpdate(
                    input: {{fullPath: "{path}", {ci_setting}: {value}}}
                    ) {{
                    ciCdSettings {{
                    {ci_setting}
                    }}
                    errors
                }}
            }}
        """,
        prefix="\n",
    )
    get_template = indent(
        """{{
            project(fullPath: "{path}") {{
                ciCdSettings {{
                   {ci_setting}
                }}
            }}
        }}""",
        prefix="\n",
    )

    def __init__(
        self,
        item: Project,
        rule: ProjectRule,
        show_diff_only: bool,
        sub_level: int = 0,
        params: Optional[GpcParameters] = None,
    ):
        super().__init__(item, rule, show_diff_only, sub_level)
        self.params = params

    def update(self):
        if "token_access" in self.rule and self.property_name in self.rule.token_access:
            change_setting = ChangeSetting(
                property_name=self.property_name,
                before=self.extract_current_setting(),
                after=self.rule.token_access[self.property_name],
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )

            if self.params.mode == RunMode.APPLY:
                new = "true" if self.rule.token_access[self.property_name] else "false"
                self.update_setting(new)

            return change_setting
        return None

    def extract_current_setting(self):
        gql = GraphqlSingleton()
        request_result = gql.run_graphql_query(
            query=self.get_template.format(
                path=self.item.attributes["path_with_namespace"], ci_setting=self.api_name
            )
        )
        return request_result["data"]["project"]["ciCdSettings"][self.api_name]

    def update_setting(self, new):
        gql = GraphqlSingleton()
        gql.run_graphql_query(
            query=self.update_template.format(
                path=self.item.attributes["path_with_namespace"],
                ci_setting=self.api_name,
                value=new,
            )
        )


class Allow_Token_Ci_Updator(TokenAccessUpdator):
    property_name = "allow_access_with_ci_job_token"
    api_name = "inboundJobTokenScopeEnabled"


class CiJobTokenScope(LocalUpdator):
    property_name = None  # type: str
    add_api = "ciJobTokenScopeAddProject"
    remove_api = "ciJobTokenScopeRemoveProject"
    direction = None  # type: str
    get_template = indent(
        """{{
        project(fullPath: "{path}") {{
            ciJobTokenScope {{
                {prop} {{
                    edges {{
                        node {{
                        fullPath
        }} }} }} }} }} }}
        """,
        prefix="",
    )
    update_template = indent(
        """mutation
                             {{{operation}(input: {{projectPath:"{path}",
                             targetProjectPath:"{targetPath}", direction: {direction}}} )
                             {{ errors }} }}""",
        prefix="",
    )

    def __init__(
        self,
        item: Project,
        rule: ProjectRule,
        show_diff_only: bool,
        sub_level: int = 0,
        params: Optional[GpcParameters] = None,
    ):
        super().__init__(item, rule, show_diff_only, sub_level)
        self.params = params
        self.errors: List[dict] = []

    @cachedproperty
    def query_property(self):
        if self.direction == "INBOUND":
            return "inboundAllowlist"
        if self.direction == "OUTBOUND":
            return "outboundAllowlist"
        return None

    def update(self):
        if "token_access" in self.rule and self.property_name in self.rule.token_access:
            before = self.extract_current_setting()
            after = self.rule.token_access[self.property_name]
            change_setting = ChangeSetting(
                property_name=self.property_name,
                before=before,
                after=after,
                show_diff_only=self.show_diff_only,
                sub_level=self.sub_level,
            )
            if self.params.mode == RunMode.APPLY:
                to_remove = set(before) - set(after)
                to_add = set(after) - set(before)
                self.update_setting(to_remove, to_add)
            return change_setting
        return None

    def update_setting(self, to_remove, to_add):
        gql = GraphqlSingleton()
        for project in to_add:
            request_result = gql.run_graphql_query(
                query=self.update_template.format(
                    operation=self.add_api,
                    path=self.item.attributes["path_with_namespace"],
                    targetPath=project,
                    direction=self.direction,
                )
            )
            errors = request_result["data"][self.add_api]["errors"]
            if errors:
                self.errors.append({"project": project, "error": errors})
        for project in to_remove:
            request_result = gql.run_graphql_query(
                query=self.update_template.format(
                    operation=self.remove_api,
                    path=self.item.attributes["path_with_namespace"],
                    targetPath=project,
                    direction=self.direction,
                )
            )
            errors = request_result["data"][self.remove_api]["errors"]
            if errors:
                self.errors.append({"project": project, "error": errors})
        if self.errors:
            raise GpcError(f"Errors updating {self.property_name}:\n {self.errors}")

    def extract_current_setting(self):
        gql = GraphqlSingleton()
        request_result = gql.run_graphql_query(
            query=self.get_template.format(
                path=self.item.attributes["path_with_namespace"], prop=self.query_property
            )
        )
        res = [
            x["node"]["fullPath"]
            for x in request_result["data"]["project"]["ciJobTokenScope"][self.query_property][
                "edges"
            ]
        ]
        res.remove(self.item.attributes["path_with_namespace"])
        return res


class AllowList(CiJobTokenScope):
    property_name = "allowed_projects"
    direction = "INBOUND"
