#!/bin/bash
tmux new-session -d -s sess1 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py AUDCAD:5 AUDCHF:5 AUDJPY:3" Enter
tmux new-session -d -s sess2 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py AUDNZD:5 AUDSGD:2 AUDUSD:5" Enter
tmux new-session -d -s sess3 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py CADCHF:5 CADJPY:3 CHFJPY:3" Enter
tmux new-session -d -s sess4 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py EURAUD:5 EURCAD:5 EURCHF:5" Enter
tmux new-session -d -s sess5 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py EURGBP:5 EURJPY:3 EURNZD:5" Enter
tmux new-session -d -s sess6 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py EURSGD:5 EURUSD:5 GBPAUD:5" Enter
tmux new-session -d -s sess7 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py GBPCAD:5 GBPCHF:5 GBPJPY:3" Enter
tmux new-session -d -s sess8 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py GBPNZD:5 GBPSGD:5 GBPUSD:5" Enter
tmux new-session -d -s sess9 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py NZDCAD:5 NZDCHF:5 NZDJPY:3" Enter
tmux new-session -d -s sess10 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py NZDUSD:5 USDCAD:5 USDCHF:5" Enter
tmux new-session -d -s sess11 \; send-keys "source shahin_v/bin/activate;python3 hook_test.py USDJPY:3 USDSGD:5 SGDJPY:3" Enter
