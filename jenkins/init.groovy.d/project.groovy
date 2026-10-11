import jenkins.model.Jenkins
import hudson.security.HudsonPrivateSecurityRealm
import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import hudson.plugins.git.GitSCM
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.UserRemoteConfig
import hudson.security.SecurityRealm

// Bootstrap only a NEW local demo controller. Never change existing security.
def instance = Jenkins.get()
if (instance.getSecurityRealm() == SecurityRealm.NO_AUTHENTICATION) {
    def passwordFile = System.getenv('VOYAGE_JENKINS_PASSWORD_FILE')
    if (!passwordFile) throw new IllegalStateException('Supply a private bootstrap password file')
    def realm = new HudsonPrivateSecurityRealm(false)
    realm.createAccount('voyage-admin', new File(passwordFile).text.trim())
    instance.setSecurityRealm(realm)
    def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
    strategy.setAllowAnonymousRead(false)
    instance.setAuthorizationStrategy(strategy)
}
instance.setNumExecutors(1)
if (instance.getItem('Voyage-Travel-CI') == null) {
    def job = instance.createProject(WorkflowJob, 'Voyage-Travel-CI')
    def scm = new GitSCM([new UserRemoteConfig('https://github.com/techysuman27/MLOps-Travel-App.git', null, null, null)],
        [new BranchSpec('*/main')], false, [], null, null, [])
    job.setDefinition(new CpsScmFlowDefinition(scm, 'Jenkinsfile'))
    job.setDescription('Individual capstone: tests, Docker build and real prediction checks. Publish/deploy require explicit parameters and credentials.')
    job.save()
}
instance.save()
