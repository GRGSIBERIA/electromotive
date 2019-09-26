module Command
    implicit none
    
contains
    subroutine CommandMode()
        use Mode, only: HelpMode
        implicit none
        integer :: count, status, length
        character(:), allocatable :: arg
        intrinsic :: command_argument_count, get_command_argument

        call get_command_argument(1, length = length, status = status)
        if (status == 0) then
            if (index(arg, "-h") > 0) then

            else if (index(arg, "-b") > 0) then

            end if
        end if
        deallocate(arg)


    
    end subroutine CommandMode

end module Command