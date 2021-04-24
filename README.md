# kc1_linux_configs
Kindle Fire Gen1 mainline linux configs

# Display Status:

#### omapdrm driver
- Working(-ish)
- Added LCD panel timings to panel-simple.c, see : `drm/panel-simple.c.patch`
- Driver is setting the wrong pixel clock
- Pixel clock should be should be ~51MHz , Instead its ~170MHz. Results in display corruption, and semi-permanent ghosting (effectivly its overclocking the panel way beyond spec, which is known to cause damage)

#### omapfb driver
- Screen OFF when linux takes control
- driver error says "cannot find video source"
- timing config seems validated
- legacy driver ?


# Related : 
kc1-linux project by Hansem Ro : https://github.com/hansemro/kc1-linux
