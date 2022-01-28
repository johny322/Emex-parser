from src.gui.threads.gui_threads import ProgressBarValueThread, ProgressBarRangeThread, EnabledStartButtonThread, \
    EndMessageThread, WarningMessageThread, InfoLabelThread

progress_bar_value_thread = ProgressBarValueThread()
progress_bar_range_thread = ProgressBarRangeThread()
enabled_start_button_thread = EnabledStartButtonThread()
end_message_thread = EndMessageThread()
warning_message_thread = WarningMessageThread()
info_label_thread = InfoLabelThread()
