# rpkg bash completion

_rpkg()
{
    COMPREPLY=()

    in_array()
    {
        local i
        for i in $2; do
            [[ $i = $1 ]] && return 0
        done
        return 1
    }

    _filedir_exclude_paths()
    {
        _filedir "$@"
        for ((i=0; i<=${#COMPREPLY[@]}; i++)); do
            [[ ${COMPREPLY[$i]} =~ /?\.git/? ]] && unset COMPREPLY[$i]
        done
    }

    local cur prev
    # _get_comp_words_by_ref is in bash-completion >= 1.2, which EL-5 lacks.
    if type _get_comp_words_by_ref &>/dev/null; then
        _get_comp_words_by_ref cur prev
    else
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
    fi

    # global options

    local options="--help -v -q"
    local options_value="--release --user --path"
    local commands="build chain-build ci clean clog clone co container-build container-build-config commit compile copr-build diff flatpak-build \
    gimmespec giturl help gitbuildhash import install lint local mockbuild mock-config new new-sources patch prep pull push retire remote scratch-build sources \
    srpm switch-branch tag unused-patches upload verify-files verrel"

    # parse main options and get command

    local command=
    local command_first=
    local path=

    local i w
    for (( i = 0; i < ${#COMP_WORDS[*]} - 1; i++ )); do
        w="${COMP_WORDS[$i]}"
        # option
        if [[ ${w:0:1} = - ]]; then
            if in_array "$w" "$options_value"; then
                ((i++))
                [[ "$w" = --path ]] && path="${COMP_WORDS[$i]}"
            fi
        # command
        elif in_array "$w" "$commands"; then
            command="$w"
            command_first=$((i+1))
            break
        fi
    done

    # complete base options

    if [[ -z $command ]]; then
        if [[ $cur == -* ]]; then
            COMPREPLY=( $(compgen -W "$options $options_value" -- "$cur") )
            return 0
        fi

        case "$prev" in
            --config)
                _filedir_exclude_paths
                ;;
            --user|-u)
                ;;
            --path)
                _filedir_exclude_paths
                ;;
            *)
                COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
                ;;
        esac

        return 0
    fi

    # parse command specific options

    local options=
    local options_target= options_arches= options_branch= options_string= options_file= options_dir= options_srpm=
    local after= after_more=

    case $command in
        help|gimmespec|gitbuildhash|giturl|lint|new|unused-patches|verrel)
            ;;
        build)
            options="--nowait --background --skip-tag --scratch --md5"
            options_arches="--arches"
            options_srpm="--srpm"
            options_target="--target"
            ;;
        chain-build)
            options="--nowait --background"
            options_target="--target"
            after="package"
            after_more=true
            ;;
        clean)
            options="--dry-run -x"
            ;;
        clog)
            options="--raw"
            ;;
        clone|co)
            options="--branches --anonymous"
            options_branch="-b"
            after="package"
            ;;
        container-build)
            options="--scratch --nowait"
            options_target="--target"
            options_string="--repo-url"
            options_arches="--arches"
            ;;
        container-build-config)
            options="--get-autorebuild"
            options_bool="--set-autorebuild"
            ;;
        commit|ci)
            options="--push --clog --raw --tag"
            options_string="--message"
            options_file="--file"
            after="file"
            after_more=true
            ;;
        compile|install)
            options="--short-circuit --nocheck"
            options_arch="--arch"
            options_dir="--builddir"
            ;;
        copr-build)
            options="--nowait"
            after="package"
            after_more=true
            ;;
        diff)
            options="--cached"
            after="file"
            after_more=true
            ;;
        flatpak-build)
            options="--scratch --nowait"
            options_target="--target"
            options_string="--repo-url"
            options_arches="--arches"
            ;;
        import)
            options="--create"
            options_branch="--branch"
            after="srpm"
            ;;
        lint)
            options="--info"
            options_file="--rpmlintconf"
            ;;
        local)
            options="--md5"
            options_arch="--arch"
            options_dir="--builddir"
            ;;
        mock-config)
            options="--target"
            options_arch="--arch"
            ;;
        mockbuild)
            options="--md5 --no-clean --no-cleanup-after --no-clean-all --shell"
            options_mroot="--root"
            ;;
        patch)
            options="--rediff"
            options_string="--suffix"
            ;;
        prep|verify-files)
            options_arch="--arch"
            options_dir="--builddir"
            ;;
        pull)
            options="--rebase --no-rebase"
            ;;
        push)
            options="--force"
            ;;
        retire)
            after_more=true
            ;;
        remote)
            options="--repo-name --remote-name"
            ;;
        scratch-build)
            options="--nowait --background --md5"
            options_target="--target"
            options_arches="--arches"
            options_srpm="--srpm"
            ;;
        sources)
            options_dir="--outdir"
            ;;
        srpm)
            options="--md5"
            ;;
        switch-branch)
            options="--list"
            after="branch"
            ;;
        tag)
            options="--clog --raw --force --list --delete"
            options_string="--message"
            options_file="--file"
            after_more=true
            ;;
        upload|new-sources)
            after="file"
            after_more=true
            ;;
    esac

    local all_options="--help $options"
    local all_options_value="$options_target $options_arches $options_branch $options_string $options_file $options_dir $options_srpm $options_bool"

    # count non-option parameters

    local i w
    local last_option=
    local after_counter=0
    for (( i = $command_first; i < ${#COMP_WORDS[*]} - 1; i++)); do
        w="${COMP_WORDS[$i]}"
        if [[ ${w:0:1} = - ]]; then
            if in_array "$w" "$all_options"; then
                last_option="$w"
                continue
            elif in_array "$w" "$all_options_value"; then
                last_option="$w"
                ((i++))
                continue
            fi
        fi
        in_array "$last_option" "$options_arches" || ((after_counter++))
    done

    # completion

    if [[ -n $options_target ]] && in_array "$prev" "$options_target"; then
        COMPREPLY=( $(compgen -W "$(_rpkg_target)" -- "$cur") )

    elif [[ -n $options_arches ]] && in_array "$last_option" "$options_arches"; then
        COMPREPLY=( $(compgen -W "$(_rpkg_arch) $all_options" -- "$cur") )

    elif [[ -n $options_srpm ]] && in_array "$prev" "$options_srpm"; then
        _filedir_exclude_paths "*.src.rpm"

    elif [[ -n $options_branch ]] && in_array "$prev" "$options_branch"; then
        COMPREPLY=( $(compgen -W "$(_rpkg_branch "$path")" -- "$cur") )

    elif [[ -n $options_file ]] && in_array "$prev" "$options_file"; then
        _filedir_exclude_paths

    elif [[ -n $options_dir ]] && in_array "$prev" "$options_dir"; then
        _filedir_exclude_paths -d

    elif [[ -n $options_bool ]] && in_array "$prev" "$options_bool"; then
        COMPREPLY=( $(compgen -W "true false" -- "$cur") )

    elif [[ -n $options_string ]] && in_array "$prev" "$options_string"; then
        COMPREPLY=( )

    else
        local after_options=

        if [[ $after_counter -eq 0 ]] || [[ $after_more = true ]]; then
            case $after in
                file)    _filedir_exclude_paths ;;
                srpm)    _filedir_exclude_paths "*.src.rpm" ;;
                branch)  after_options="$(_rpkg_branch "$path")" ;;
                package) after_options="$(_rpkg_package "$cur")";;
            esac
        fi

        if [[ $cur != -* ]]; then
            all_options=
            all_options_value=
        fi

        COMPREPLY+=( $(compgen -W "$all_options $all_options_value $after_options" -- "$cur" ) )
    fi

    return 0
} &&
complete -F _rpkg rpkg

_rpkg_target()
{
    koji list-targets --quiet 2>/dev/null | cut -d" " -f1
}

_rpkg_arch()
{
    echo "i386 x86_64 ppc ppc64 s390 s390x sparc sparc64"
}

_rpkg_branch()
{
    local git_options= format="--format %(refname:short)"
    [[ -n $1 ]] && git_options="--git-dir=$1/.git"

    git $git_options for-each-ref $format 'refs/remotes' | sed 's,.*/,,'
    git $git_options for-each-ref $format 'refs/heads'
}

_rpkg_package()
{
    repoquery -C --qf=%{sourcerpm} "$1*" 2>/dev/null | sort -u | sed -r 's/(-[^-]*){2}\.src\.rpm$//'
}

# Local variables:
# mode: shell-script
# sh-basic-offset: 4
# sh-indent-comment: t
# indent-tabs-mode: nil
# End:
# ex: ts=4 sw=4 et filetype=sh
