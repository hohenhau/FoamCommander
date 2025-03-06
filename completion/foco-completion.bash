# Bash completion function for 'foco'
_foco_complete()
{
    # Variables that bash-completion uses internally
    local cur prev words cword
    # Initialize bash completion state.
    _init_completion || return
    
    # Get the tool directory (assumes foco is in the PATH and next to tools/).
    TOOL_DIR="$(dirname $(which foco))/tools"
    
    # If completing the first argument (command name), suggest tool names only.
    if [[ $COMP_CWORD -eq 1 ]]; then
        # Force file-only completion, no directories
        compopt -o nospace -o filenames
        
        # List available tools (exclude directories and .py extensions)
        tools=$(find "$TOOL_DIR" -maxdepth 1 -type f -not -path "${TOOL_DIR}/utilities/*" | xargs basename | sed 's/\.py$//g')
        
        COMPREPLY=($(compgen -W "$tools" -- "$cur"))
        return
    fi
    
    # For argument completion, first get the current command
    local cmd="${COMP_WORDS[1]}"
    
    # Debug output - uncomment if needed
    # echo "Command: $cmd, Previous: $prev, Current: $cur" >&2
    
    # Special handling for specific commands' arguments
    case "$cmd" in
        estimateInternalFields|prepare)
            # Define available arguments
            local opts="-hydraulic_diameter -free_stream_velocity -kinematic_viscosity -reynolds_number -turbulence_intensity"
            
            # If previous word is an option needing a value, don't offer completions
            if [[ "$prev" == -* ]]; then
                COMPREPLY=()
                return
            fi
            
            # Filter out already used options
            for ((i=2; i < ${#COMP_WORDS[@]}; i++)); do
                if [[ "${COMP_WORDS[i]}" == -* ]]; then
                    opts=${opts/${COMP_WORDS[i]}/}
                fi
            done
            
            # Only suggest options for current word
            COMPREPLY=($(compgen -W "$opts" -- "$cur"))
            ;;
            
        *)
            # For other commands, no argument suggestions
            COMPREPLY=()
            ;;
    esac
}

# Register completion function for 'foco' command.
complete -o nospace -o filenames -F _foco_complete foco