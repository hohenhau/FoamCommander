# Bash completion function for 'foco'
_foco_complete()
{
    # Variables that bash-completion uses internally
    local cur prev words cword
    
    # Initialize bash completion state.
    _init_completion || return
    
    # Get tool directory (assumes foco is in the PATH and next to tools/).
    TOOL_DIR="$(dirname $(which foco))/tools"
    
    # List available tools (remove `.py` extensions to match user commands).
    tools=$(ls "$TOOL_DIR" | sed 's/\.py$//g')
    
    # If completing the first argument (command name), suggest tool names.
    if [[ $COMP_CWORD -eq 1 ]]; then
        COMPREPLY=($(compgen -W "$tools" -- "$cur"))
    
    # Special handling for argument completion for specific tools
    elif [[ "${COMP_WORDS[1]}" == "estimateInternalFields" || "${COMP_WORDS[1]}" == "prepare" ]]; then
        COMPREPLY=($(compgen -W "-hydraulic_diameter -free_stream_velocity -kinematic_viscosity -reynolds_number -turbulence_intensity" -- "$cur"))
    else
        # For other commands, no argument hints (you could extend this later if needed).
        COMPREPLY=()
    fi
}

# Register completion function for 'foco' command.
complete -F _foco_complete foco