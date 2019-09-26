module Mode
    implicit none
    
contains
    subroutine HelpMode()
        implicit none
        print *, "electromotive.exe [option] [json config file]"
        PRINT *, "[options]"
        PRINT *, "Choose which one."
        PRINT *, "    -b    Generates .brp (binary report) files from json."
        PRINT *, "    -w    Analyses electromotive."
        PRINT *, "    -h    Shows help."
        PRINT *, "[json config file]"
        PRINT *, "    This is require option."
    end subroutine HelpMode
end module Mode