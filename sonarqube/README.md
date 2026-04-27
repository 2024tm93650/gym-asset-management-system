# SonarQube — local setup for ACEest Fitness

## 1. Start the SonarQube stack

```bash
cd sonarqube
docker compose up -d
# wait ~60s for SonarQube to fully boot, then open:
open http://localhost:9001
```

First-time login: `admin / admin` → you will be forced to set a new password.

## 2. Create the project + token

1. **Projects → Create Project → Manually**
   - Project display name: `ACEest Fitness & Gym`
   - Project key: `aceest-fitness`   *(must match `sonar.projectKey` in `sonar-project.properties`)*
2. **Set Up → Locally → Generate a token**
   - Name: `aceest-jenkins-token`, Expires in: 90 days
   - **Copy the token** (starts with `sqp_…` or `squ_…`) — you only see it once.
3. Choose analysis method **"Other (for JS, TS, Go, Python, PHP, ...)"** → **Linux**.

## 2b. Add the token to Jenkins

Manage Jenkins → Credentials → (global) → Add Credentials
| Field   | Value                              |
|---------|------------------------------------|
| Kind    | Secret text                        |
| Secret  | *(the token you just copied)*      |
| ID      | `sonarqube-token`                  |

## 3. (Optional) Run a scan locally first to verify

```bash
docker run --rm \
  -e SONAR_HOST_URL="http://host.docker.internal:9001" \
  -e SONAR_TOKEN="sqp_xxx_paste_token" \
  -v "$PWD:/usr/src" \
  sonarsource/sonar-scanner-cli:latest
```

Open `http://localhost:9001/dashboard?id=aceest-fitness` to see the result.

## 4. Run via Jenkins

The pipeline now has a **SonarQube Analysis** stage that:
- Runs `sonarsource/sonar-scanner-cli` as a throwaway container (no install on Jenkins)
- Uses the `sonarqube-token` credential
- Sends results to `http://host.docker.internal:9001`

Just hit **Build Now** in Jenkins and watch the stage turn green. When it finishes,
the SonarQube dashboard will show:
- Bugs / Vulnerabilities / Code Smells
- Coverage (from `reports/coverage.xml`)
- Duplications
- Quality Gate result
