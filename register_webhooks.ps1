$WEBHOOK_URL = "https://371d-102-129-89-238.ngrok-free.app/github/webhook"
$SECRET = "0c995e8ef0b8ba3d97665a6c140b945d647a6f847c60ac1d6d5088d4bf7ca607"

# Only register on repos you personally own or orgs you control
$TARGET_OWNERS = @("bruxx-6243", "brx-hashcode")

$repos = gh api user/repos --paginate --jq ".[] | select(.archived == false and .fork == false) | .full_name" 2>&1

foreach ($repo in $repos) {
    $owner = $repo.Split("/")[0]
    if ($TARGET_OWNERS -notcontains $owner) {
        continue
    }

    # Skip if webhook already exists
    $existing = gh api "repos/$repo/hooks" --jq ".[].config.url" 2>&1
    if ($existing -like "*$WEBHOOK_URL*") {
        Write-Host "SKIP (already exists): $repo"
        continue
    }

    $result = gh api "repos/$repo/hooks" --method POST `
        -f "config[url]=$WEBHOOK_URL" `
        -f "config[secret]=$SECRET" `
        -f "config[content_type]=json" `
        -f "events[]=issues" `
        -f "events[]=issue_comment" `
        -f "events[]=pull_request" `
        -F "active=true" 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK: $repo"
    } else {
        Write-Host "FAIL: $repo — $result"
    }
}
