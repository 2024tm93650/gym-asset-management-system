# Jenkins setup for ACEest Fitness & Gym

This folder spins up a local Jenkins controller (LTS, JDK17) for the assignment.

## 1. Start Jenkins

```bash
cd jenkins
docker compose up -d
docker exec aceest-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Open http://localhost:8080 → paste the initial admin password → install **Suggested plugins**.

## 2. Install required plugins

Manage Jenkins → Plugins → Available, install (if not already there):

- Pipeline
- Git
- Docker Pipeline
- Credentials Binding
- HTML Publisher
- JUnit
- SonarQube Scanner (only if you'll wire SonarQube)

## 3. Install required tools inside the container

The pipeline shells out to `python3`, `docker`, `curl`, `kubectl` (optional), `sonar-scanner` (optional).
Inside the running Jenkins container:

```bash
docker exec -u root aceest-jenkins bash -lc '
  apt-get update &&
  apt-get install -y python3 python3-venv python3-pip docker.io curl &&
  # kubectl (optional, only for the Deploy stage)
  curl -L "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/$(dpkg --print-architecture)/kubectl" -o /usr/local/bin/kubectl &&
  chmod +x /usr/local/bin/kubectl
'
```

## 4. Add credentials

Manage Jenkins → Credentials → System → Global → Add Credentials:

| Kind                | ID                | Value                                   |
|---------------------|-------------------|-----------------------------------------|
| Username + password | `dockerhub-creds` | username `2024tm93650`, password is the Docker Hub PAT |
| Secret text         | `sonarqube-token` | `sqp_xxx` from SonarQube (optional)     |
| Secret file         | `kubeconfig`      | upload your `~/.kube/config` (optional) |

## 5. Create the pipeline job

New Item → **Pipeline** → name `aceest-fitness-pipeline` → OK.

In the job config:

- **Build Triggers** → tick *Poll SCM* with `H/2 * * * *`  (matches the `Jenkinsfile`)
- **Pipeline** → Definition: *Pipeline script from SCM*
  - SCM: Git
  - Repository URL: `https://github.com/2024tm93650/gym-asset-management-system.git`
  - Branch: `*/main`
  - Script Path: `Jenkinsfile`

Save → **Build Now**.
