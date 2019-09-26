module Mode
    implicit none
    
contains
    subroutine HelpMode()
        implicit none
        print *, "electromotive.exe [option] [json config file]"
        PRINT *, "[options]"
        PRINT *, "Choose which one."
        PRINT *, "    -e    Analysis electromotive from json."
        PRINT *, "    -i    Analysis to induce elements from magnets."
        PRINT *, "    -h    Shows help."
        PRINT *, "[json config file]"
        PRINT *, "    This is require option."
    end subroutine HelpMode

    ! 誘導起電力を計算する
    subroutine ElectromotiveMode(jsonpath)
        implicit none
        character(*) :: jsonpath

    end subroutine

    ! 要素ごとに磁化した量を表示する
    subroutine InduceElementMode(jsonpath)
        implicit none
        character(*) :: jsonpath

    end subroutine

end module Mode