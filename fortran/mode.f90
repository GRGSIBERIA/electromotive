module Mode
    implicit none
    
contains
    subroutine HelpMode()
        implicit none
        print *, "electromotive.exe [option] [config file]"
        PRINT *, "[options]"
        PRINT *, "Choose which one."
        PRINT *, "    -e    Analysis the electromotive from the configure file."
        PRINT *, "    -h    Shows a help."
        PRINT *, "[config file]"
        PRINT *, "    This is require option."
    end subroutine HelpMode


    ! 誘導起電力を計算する
    subroutine ElectromotiveMode(confpath)
        implicit none
        character(*) :: confpath
        integer, parameter :: fd = 100

        open(fd, file=confpath, status="old")

        close(fd)

    end subroutine

    
    ! 要素ごとに磁化した量を表示する
!    subroutine InduceElementMode(confpath)
!        implicit none
!        character(*) :: confpath
!
!    end subroutine

end module Mode