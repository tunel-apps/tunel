if [[ -f "$HOME/.bash_profile" ]]; then
    echo "Sourcing ~/.bash_profile"
    source $HOME/.bash_profile
elif [[ -f "$HOME/.profile" ]]; then
    echo "Sourcing ~/.profile"
    source $HOME/.profile
else
   echo "Cannot find $HOME/.bash_profile or $HOME/.profile"
fi
