# Desc: Batch train all models for v80m dataset
#
# Usage: bash _batch_train.sh
#

# bash _train.sh train_80m.py v0_80m_nodem_nolatlon.json  &&
# bash _train.sh train_80m.py v0_80m_nodem.json  &&
# bash _train.sh train_80m.py v0_80m_nodem_nolatlon_l1c.json  &&
# bash _train.sh train_80m.py v0_80m_l2a_b10.json  &&
# bash _train.sh train_40m.py v0_40m.json  &&
# bash _train.sh train_40m.py v0_40m_nodem_nolatlon.json  &&
# bash _train.sh train_40m.py v0_40m_nodem.json  &&
# bash _train.sh train_40m.py v0_40m_l2a_b10.json  


# bash _train.sh train_80m.py v0_80m_nodem_nolatlon_nob9.json &&
# bash _train.sh train_80m.py v0_80m_nodem_nolatlon_nob9_mobnet.json &&
# bash _train.sh train_80m.py v0_80m_nodem_nolatlon_nob9_ce.json &&
# bash _train.sh train_80m.py v0_80m_nodem_nolatlon_nob9_mobnet_sigmoid_ce.json

bash _train.sh trainer.py configs/lcm10-unet-base-v08+.json &&
sleep 10 &&
bash _train.sh trainer.py configs/lcm10-unet-base-v08.json &&
sleep 10 &&
bash _train.sh trainer.py configs/lcm10-unet-base-v09+.json &&
sleep 10 &&
bash _train.sh trainer.py configs/lcm10-unet-base-v09.json &&
sleep 10 &&
bash _train.sh trainer.py configs/lcm10-unet-base-v10+.json &&
sleep 10 &&
bash _train.sh trainer.py configs/lcm10-unet-base-v10.json

