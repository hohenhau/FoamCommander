#!/bin/bash

# Bash completion function for 'foco'
_foco_complete() {
    local cur prev words cword
    _init_completion -s || return

    TOOL_DIR="$(dirname "$(command -v foco)")/tools"

    # Command name completion (first argument)
    if (( COMP_CWORD == 1 )); then
        compopt -o nospace
        
        # Get base filenames without extensions or directories
        local tools
        tools=$(find "$TOOL_DIR" -maxdepth 1 -type f \( ! -name ".*" \) -not -path "${TOOL_DIR}/utilities/*" \
            -exec basename {} \; | sed -E 's/\.[^.]+$//')
        
        COMPREPLY=($(compgen -W "$tools" -- "$cur"))
        return
    fi

    local cmd="${COMP_WORDS[1]}"
    case "$cmd" in
        estimateInternalFields|prepare)
            # Available options with metadata
            local opts=(
                '-hydraulic_diameter:Specify hydraulic diameter'
                '-free_stream_velocity:Set free stream velocity'
                '-kinematic_viscosity:Define kinematic viscosity'
                '-reynolds_number:Input Reynolds number'
                '-turbulence_intensity:Specify turbulence intensity'
            )

            # Filter used options using array operations
            for existing_opt in "${COMP_WORDS[@]:2}"; do
                for i in "${!opts[@]}"; do
                    [[ "${opts[i]%%:*}" == "$existing_opt" ]] && unset -v 'opts[i]'
                done
            done

            # Generate completion with descriptions
            if [[ -n "$cur" ]]; then
                COMPREPLY=($(printf '%s\n' "${opts[@]}" | compgen -W "$(printf '%s ' "${opts[@]}")" -- "$cur"))
            else
                COMPREPLY=("${opts[@]}")
            fi
            compopt -o nospace -o nosort
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

complete -o nospace -F _foco_complete foco
