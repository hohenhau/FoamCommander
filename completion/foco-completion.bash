#!/bin/bash
# Bash completion function for 'foco'
_foco_complete() {
    local cur prev words cword
    _init_completion -s || return
    
    # Specify the program's command name
    COMMAND_NAME="foco"
    
    # Find the executable location
    COMMAND_PATH=$(command -v $COMMAND_NAME)
    
    if [ -z "$COMMAND_PATH" ]; then
        return # Command not found in PATH
    fi
    
    # Find the base directory where the command is located
    BASE_DIR="$(dirname "$COMMAND_PATH")"
    
    # Tools directory should be in the same parent directory
    TOOL_DIR="$BASE_DIR/tools"
    
    # Check if tools directory exists
    if [ ! -d "$TOOL_DIR" ]; then
        return # Tools directory not found
    fi
    
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
                '-hydraulic_diameter'
                '-free_stream_velocity'
                '-kinematic_viscosity'
                '-reynolds_number'
                '-turb_intensity'
                '-turb_kinetic_energy'
                '-turb_length_scale'
                '-turb_dissipation_rate'
                '-specific_dissipation'
                '-turb_viscosity'
            )
            # Filter used options using array operations
            for existing_opt in "${COMP_WORDS[@]:2}"; do
                for i in "${!opts[@]}"; do
                    [[ "${opts[i]%%:*}" == "$existing_opt" ]] && unset -v 'opts[i]'
                done
            done
            # Generate completion with descriptions
            if [[ -n "$cur" ]]; then  # If user has started typing show matching options
                COMPREPLY=($(printf '%s\n' "${opts[@]}" | compgen -W "$(printf '%s ' "${opts[@]}")" -- "$cur"))
            else  # If user has not started typing show all options
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
