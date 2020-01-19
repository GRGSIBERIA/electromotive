module Command
    implicit none
    
contains
    subroutine CommandMode()
        use Mode, only: HelpMode, ElectromotiveMode
        implicit none
        integer :: status, length, count
        character(:), allocatable :: execmode
        character(:), allocatable :: confpath
        !intrinsic :: command_argument_count, get_command_argument  ! 警告が出る

        count = command_argument_count()
        if (count == 2) then
            call get_command_argument(1, length = length, status = status)

            ! コマンドライン引数を取得する手続き
            if (status == 0) then
                allocate(character(length) :: execmode)
                call get_command_argument(1, execmode, status = status)

                call get_command_argument(2, confpath, length = length, status = status)
                if (status == 0) then
                    allocate(character(length) :: confpath)
                    call get_command_argument(2, confpath, status = status)
                else
                    call HelpMode()
                    stop
                end if
            else
                call HelpMode()
                stop
            end if

            ! モードごとに分岐
            if (index(execmode, "-h") > 0) then
                CALL HelpMode()

            else if (index(execmode, "-e") > 0) then
                CALL ElectromotiveMode(confpath)

!            else if (index(execmode, "-i") > 0) then
!                CALL InduceElementMode(confpath)

            end if

            deallocate(execmode)
            deallocate(confpath)
        else
            Call HelpMode()
            stop
        end if
    end subroutine CommandMode

end module Command