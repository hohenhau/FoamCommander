# Bash completion function for 'foco'
_foco_complete()
{
    # Variables that bash-completion uses internally
    local cur prev words cword
    # Initialize bash completion state.
    _init_completion || return
    
    # Get the tool directory (assumes foco is in the PATH and next to tools/).
    TOOL_DIR="$(dirname $(which foco))/tools"
    
    # If completing the first argument (command name), suggest tool names.
    if [[ $COMP_CWORD -eq 1 ]]; then
        # List available tools (remove .py extensions to match user commands).
        tools=$(find "$TOOL_DIR" -maxdepth 1 -type f -not -path "${TOOL_DIR}/utilities/*" | sed 's/\.py$//g' | sed 's|'"${TOOL_DIR}"'/||g')
        COMPREPLY=($(compgen -W "$tools" -- "$cur"))
        return
    fi
    
    # Get the current command
    local cmd="${COMP_WORDS[1]}"
    
    # Handle different commands
    case "$cmd" in
        estimateInternalFields|prepare)
            # Define all possible options
            local opts="-hydraulic_diameter -free_stream_velocity -kinematic_viscosity -reynolds_number -turbulence_intensity"
            
            # If the previous word is an option that requires a value, don't suggest options
            if [[ "$prev" == -* ]]; then
                # Previous word is an option, so we're expecting a value
                COMPREPLY=()
                return
            fi
            
            # Filter out options that have already been used
            local used_opts=""
            for ((i=2; i < ${#COMP_WORDS[@]}; i++)); do
                if [[ "${COMP_WORDS[i]}" == -* ]]; then
                    used_opts+=" ${COMP_WORDS[i]}"
                fi
            done
            
            # Remove used options from available options
            for opt in $used_opts; do
                opts=${opts/$opt/}
            done
            
            # Only suggest remaining options if current word starts with '-'
            if [[ "$cur" == -* || "$cur" == "" ]]; then
                COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            else
                COMPREPLY=()
            fi
            ;;
        *)
            # For other commands, no argument hints
            COMPREPLY=()
            ;;
    esac
}

# Register completion function for 'foco' command.
complete -F _foco_complete foco