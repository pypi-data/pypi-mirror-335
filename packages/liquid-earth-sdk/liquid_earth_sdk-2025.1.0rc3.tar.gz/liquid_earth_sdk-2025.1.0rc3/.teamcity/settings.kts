import jetbrains.buildServer.configs.kotlin.*
import jetbrains.buildServer.configs.kotlin.buildFeatures.PullRequests
import jetbrains.buildServer.configs.kotlin.buildFeatures.commitStatusPublisher
import jetbrains.buildServer.configs.kotlin.buildFeatures.perfmon
import jetbrains.buildServer.configs.kotlin.buildFeatures.pullRequests
import jetbrains.buildServer.configs.kotlin.buildSteps.script
import jetbrains.buildServer.configs.kotlin.projectFeatures.githubIssues
import jetbrains.buildServer.configs.kotlin.triggers.vcs

/*
The settings script is an entry point for defining a TeamCity
project hierarchy. The script should contain a single call to the
project() function with a Project instance or an init function as
an argument.

VcsRoots, BuildTypes, Templates, and subprojects can be
registered inside the project using the vcsRoot(), buildType(),
template(), and subProject() methods respectively.

To debug settings scripts in command-line, run the

    mvnDebug org.jetbrains.teamcity:teamcity-configs-maven-plugin:generate

command and attach your debugger to the port 8000.

To debug in IntelliJ Idea, open the 'Maven Projects' tool window (View
-> Tool Windows -> Maven Projects), find the generate task node
(Plugins -> teamcity-configs -> teamcity-configs:generate), the
'Debug' option is available in the context menu for the task.
*/

version = "2024.12"

project {

    buildType(TestingDev001)

    features {
        githubIssues {
            id = "PROJECT_EXT_4"
            displayName = "terranigma-solutions/liquid_earth_python_sdk"
            repositoryURL = "https://github.com/terranigma-solutions/liquid_earth_python_sdk"
            param("tokenId", "")
        }
    }
}

object TestingDev001 : BuildType({
    name = "Testing Dev 001"

  params {
        // Backend configuration
        param("env.BACKEND_OVERRIDE_DEV", "https://liquidearthapim-dev001.azure-api.net/python/")
        param("env.BACKEND_OVERRIDE_LOCAL", "http://localhost:7151/api")
        param("env.BACKEND_OVERRIDE", "%env.BACKEND_OVERRIDE_DEV%")
        
        // API Tokens
        password("env.LIQUID_EARTH_API_TOKEN_DEV001", "credentialsJSON:e740f821-25ac-410c-9f81-2b8cb7c7911e")
        password("env.LIQUID_EARTH_API_TOKEN_LEGACY", "credentialsJSON:e740f821-25ac-410c-9f81-2b8cb7c7911e")
        password("env.LIQUID_EARTH_API_TOKEN_REVEAL", "credentialsJSON:d14b7073-3cd7-4e10-a829-2a094b2576a8")
        param("env.LIQUID_EARTH_API_TOKEN", "%env.LIQUID_EARTH_API_TOKEN_DEV001%")
        
        // Login configuration
        password("env.LOGIN_PASSWORD", "credentialsJSON:d61e0721-071f-4838-9940-145fe0709afd")
        param("env.LOGIN_URL", "https://liquidearthapim-dev001.azure-api.net/user/login_b2c_license")
        param("env.LOGIN_USER", "miguel@terranigma-solutions.com")
        param("env.LOGIN_CLIENT_ID", "685e08c0-0aac-42f6-80a9-c57440cd2962")
        param("env.LOGIN_SCOPE", "%env.LOGIN_CLIENT_ID%")
        param("env.LOGIN_SUBSCRIPTION_KEY", "0d7113b9f2054be8b4e1b350f18a7f72")
        
        // Path configurations
        param("env.DXF_DATA_PATH", "%env.TERRA_PATH_DEVOPS%/meshes/upc_surface.dxf")
        param("env.DXF_DATA_PATH_II", "%env.TERRA_PATH_DEVOPS%/meshes/leinster_detector_positions.dxf")
        param("env.PATH_TO_MX", "%env.TERRA_PATH_DEVOPS%/volume/GOCAD/mix/horizons_faults.mx")
        param("env.PATH_TO_DXF_DATA_PATH_SMALL", "%env.TERRA_PATH_DEVOPS%/meshes/shafts_small.dxf")
        
        // Test user configuration
        param("env.TEST_USER_ID", "43773b72-feae-495d-a1d9-e529dc64da9f")
        param("env.TEST_LOGIN_TOKEN", "Not sure how to set this yet")
        
        // Additional parameters
        param("env.TERRA_PATH_DEVOPS", "Not set")
    }    
    vcs {
        root(DslContext.settingsRoot)
    }

    steps {
        script {
            name = "Setup"
            id = "Setup"
            scriptContent = """
                @echo on
                python -m venv venv
                call venv\Scripts\activate
                venv\Scripts\python -m pip install --upgrade pip
                
                echo Checking directory...
                dir
                dir .requirements
                
                venv\Scripts\pip install --verbose -r requirements/requirements.txt
                venv\Scripts\pip install --verbose teamcity-messages
            """.trimIndent()
        }
        script {
            name = "Run Test: Core"
            id = "Run_Test"
            scriptContent = """
                @echo on
                venv\Scripts\python -m pytest --teamcity -v
            """.trimIndent()
        }
        script {
            name = "Run Test: Mesh"
            id = "Run_Test_2"
            enabled = false
            executionMode = BuildStep.ExecutionMode.RUN_ON_FAILURE
            scriptContent = """
                venv\Scripts\pip install --verbose -r requirements/requirements_mesh.txt
                
                @echo on
                set REQUIREMENT_LEVEL=READ_MESH
                echo REQUIREMENT_LEVEL is %REQUIREMENT_LEVEL%
                venv\Scripts\python -m pytest --teamcity -v -m read_mesh
            """.trimIndent()
        }
    }

    triggers {
        vcs {
            branchFilter = """
                +pr: draft=false
                -:refs/heads/main
                -:<default>
            """.trimIndent()
        }
    }

    features {
        perfmon {
        }
        commitStatusPublisher {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            publisher = github {
                githubUrl = "https://api.github.com"
                authType = personalToken {
                    token = "credentialsJSON:4df4bdb0-1278-4834-a702-18ae3a286003"
                }
            }
        }
        pullRequests {
            vcsRootExtId = "${DslContext.settingsRoot.id}"
            provider = github {
                authType = token {
                    token = "credentialsJSON:4df4bdb0-1278-4834-a702-18ae3a286003"
                }
                filterAuthorRole = PullRequests.GitHubRoleFilter.MEMBER
            }
        }
    }
})
