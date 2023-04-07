import dmx.dmx_comm as dmx
dm = dmx.DmxPy('COM3')
dm.blackout()
dm.render()