Attributes {
    NC_GLOBAL {
        String title "WAVE_nww3 Global wave model fcst from 18Z21may2015, downloaded May 21 23:19 UTC";
        String Conventions "COARDS", "GrADS";
        String dataType "Grid";
        String history "Wed May 27 07:13:28 UTC 2015 : imported by GrADS Data Server 2.0";
    }
    lon {
        String grads_dim "x";
        String grads_mapping "linear";
        String grads_size "288";
        String units "degrees_east";
        String long_name "longitude";
        Float64 minimum 0.00000000000;
        Float64 maximum 358.75000000000;
        Float32 resolution 1.25;
    }
    lat {
        String grads_dim "y";
        String grads_mapping "linear";
        String grads_size "157";
        String units "degrees_north";
        String long_name "latitude";
        Float64 minimum -78.00000000000;
        Float64 maximum 78.00000000000;
        Float32 resolution 1.0;
    }
    time {
        String grads_dim "t";
        String grads_mapping "linear";
        String grads_size "61";
        String grads_min "18z21may2015";
        String grads_step "3hr";
        String units "days since 1-1-1 00:00:0.0";
        String long_name "time";
        String minimum "18z21may2015";
        String maximum "06z29may2015";
        Float32 resolution 0.125;
    }
    dirpwsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none primary wave direction [deg] ";
    }
    dirswsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none secondary wave direction [deg] ";
    }
    htsgwsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none significant height of combined wind waves and swell [m] ";
    }
    perpwsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none primary wave mean period [s] ";
    }
    perswsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none secondary wave mean period [s] ";
    }
    ugrdsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none u-component of wind [m/s] ";
    }
    vgrdsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none v-component of wind [m/s] ";
    }
    wdirsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none wind direction (from which blowing) [deg] ";
    }
    windsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none wind speed [m/s] ";
    }
    wvdirsfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none direction of wind waves [deg] ";
    }
    wvpersfc {
        Float32 _FillValue 9.999E20;
        Float32 missing_value 9.999E20;
        String long_name "** surface none mean period of wind waves [s] ";
    }
}
