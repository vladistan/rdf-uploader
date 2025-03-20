#!/bin/bash

# Borrowed from : https://github.com/Autorevision/autorevision/blob/master/autorevision.sh
function gitRepo {

    set +e +o pipefail
    local oldPath="$(pwd)"

    cd "$(git rev-parse --show-toplevel)"

    local currentRev="$(git rev-parse HEAD)"

    # Is the working copy clean?
    test -z "$(git status --untracked-files=normal --porcelain)"
    VCS_WC_MODIFIED="${?}"

    # Enumeration of changesets
    VCS_NUM="$(git rev-list --count "${currentRev}" 2>/dev/null)"
    if [ -z "${VCS_NUM}" ]; then
        VCS_NUM="$(git rev-list HEAD | wc -l)"
    fi

    # The short hash
    VCS_SHORT_HASH="$(git rev-parse --short "${currentRev}")"

    # Cache the description
    local DESCRIPTION="$(git describe --long --tags "${currentRev}" 2>/dev/null)"
    # Current or last tag ancestor (empty if no tags)
    VCS_TAG="$(echo "${DESCRIPTION}" | sed -e "s:-g${VCS_SHORT_HASH}\$::" -e 's:-[0-9]*$::')"
    # Distance to last tag or an alias of VCS_NUM if there is no tag
    if [ -n "${DESCRIPTION}" ]; then
        VCS_TICK="$(echo "${DESCRIPTION}" | sed -e "s:${VCS_TAG}-::" -e "s:-g${VCS_SHORT_HASH}::")"
    else
        VCS_TICK="${VCS_NUM}"
    fi

    cd "${oldPath}"

    set -e -o pipefail

}

echo "Survey git repo"
gitRepo


VERSION="${VCS_TAG#v}.${VCS_TICK}"

# Add -local and timestamp to version if running locally (not in GitHub Actions)
if [ -z "$GITHUB_ACTION" ]; then
    TIMESTAMP=$(date +"%Y%m%d%H%M%S")
    VERSION="${VERSION}-local${TIMESTAMP}"
fi

if [ "$VCS_WC_MODIFIED" == 1 ]; then
    VERSION="${VERSION}-dirty"
fi

# Add PR number to version string if this is a pull request
if [ "$GITHUB_EVENT_NAME" == "pull_request" ]; then
    # Extract PR number from GITHUB_REF
    PR_NUMBER=$(echo $GITHUB_REF | sed -n 's/refs\/pull\/\([0-9]*\)\/merge/\1/p')
    if [ -n "$PR_NUMBER" ]; then
        VERSION="${VERSION}+pr${PR_NUMBER}"
        VERSION_2="${VERSION}.g${VCS_SHORT_HASH}"
    fi
fi

cat <<EOF
  /\_/\     Version   : ${VERSION}
 ( o.o )    Commit    : ${VCS_SHORT_HASH}
  > ^ <

EOF

if [ -n "$VERSION_2" ]; then
    echo "Extra Version   : ${VERSION_2}"
fi

if [ -n "$GITHUB_OUTPUT" ]; then
    if [ -n "$VERSION_2" ]; then
        echo "version=${VERSION_2}" >> $GITHUB_OUTPUT
    else
        echo "version=${VERSION}" >> $GITHUB_OUTPUT
    fi
fi
