program electromotive
    use Command
    implicit none
    
    call MAIN()

    contains
    
    subroutine MAIN()
        call CommandMode()
    end subroutine
end program electromotive