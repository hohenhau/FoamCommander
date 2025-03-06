#!/bin/bash

# Bash completion function for 'foco'
_foco_complete()
{
    # Variables that bash-completion uses internally
    local cur prev words cword
    # Initialize bash completion state.
    _init_completion || return
    
    # Get the tool directory (assumes foco is in the PATH and next to tools/)
    TOOL_DIR="$(dirname "$(which foco)")/tools"
    
    # If completing the first argument (command name), suggest tool names only
    if [[ $COMP_CWORD -eq 1 ]]; then
        compopt -o nospace  # Disable filename completion
        
        # List available tools (exclude directories and .py extensions)
        local tools
        tools=$(find "$TOOL_DIR" -maxdepth 1 -type f -not -path "${TOOL_DIR}/utilities/*" \
            | xargs -I{} basename {} .py)
        
        COMPREPLY=($(compgen -W "$tools" -- "$cur"))
        return
    fi
    
    # For argument completion, first get the current command
    local cmd="${COMP_WORDS[1]}"
    
    # Special handling for specific commands' arguments
    case "$cmd" in
        estimateInternalFields|prepare)
            # Define available arguments as array
            local opts=(-hydraulic_diameter -free_stream_velocity 
                       -kinematic_viscosity -reynolds_number 
                       -turbulence_intensity)
            
            # Filter out already used options
            for word in "${COMP_WORDS[@]:2}"; do
                if [[ "$word" == -* ]]; then
                    # Remove matching option from array
                    opts=("${opts[@]/$word/}")
                fi
            done
            
            # Clean up empty array elements
            opts=("${opts[@]}")
            
            COMPREPLY=($(compgen -W "${opts[*]}" -- "$cur"))
            ;;
            
        *)
            # For other commands, no argument suggestions
            COMPREPLY=()
            ;;
    esac
}

# Register completion function for 'foco' command
complete -o nospace -F _foco_complete foco
