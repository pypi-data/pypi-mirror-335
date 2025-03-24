"""
CloudSat pre-process module
"""

from ..satellite_general import Preparation

class CloudSat(Preparation):
    def __init__(self,work_path=None,lat_range=[-10,50],lon_range=[90,180],time_period=['200606'],data_path='/data/dadm1/obs/CloudSat'):
        from pathlib import Path
        super().__init__(work_path,lat_range,lon_range,time_period)
        if self.work_path == None or self.work_path == []:
            self.work_path = Path().cwd()
        self.data_path = data_path

    def product_list(self):
        print('CloudSat product on 107') 
        print('hdf-GEOPROF; hdf-GEOPROF-LIDAR; hdf-FLXHR-LIDAR') 
  
    def generate_list(self,product_name,time_period,period_output=False):
        import glob as glob
        product_name = self.check_list(product_name)
        time_period = self.check_list(time_period) 
        year_list, ju_day_list, start_end_hour_list = self.convert_input_period(time_period)  
        search_period = self.generate_period(year_list, ju_day_list, start_end_hour_list)
        full_path_file_list = []
        for product in product_name:
            for hdf_time in search_period:
                product_path = self.data_path +'/'+ product +'/'+ hdf_time[0:4] + '/'
                target_file = product_path + hdf_time + '*'+ '.hdf'
                search_files = sorted(glob.glob(target_file))
                full_path_file_list.extend(search_files)
        if len(full_path_file_list) < 1:
           print('No .hdf file detected!')
        if period_output: 
            return(full_path_file_list,search_period)
        else:
            return(full_path_file_list)

    def sub_domain_check(self,full_path_file_list,extracted_lon_range=[],extracted_lat_range=[],mask_output=False):
        import numpy as np
        full_path_file_list = self.check_list(full_path_file_list)
        region_mask_list = []
        era5_lon_list = []
        era5_lat_list = []
        sub_domain_file_list = []
        if len(full_path_file_list) > 0:
            var_name = ['Longitude','Latitude','Data_quality']
            lon_list = self.read_ori_vdata(full_path_file_list,var_name[0])
            lat_list = self.read_ori_vdata(full_path_file_list,var_name[1])
            qua_list = self.read_ori_vdata(full_path_file_list,var_name[2])
            print('Check CloudSat track pass the traget domain')

            for i in range(0,len(lon_list)):
                region_mask,era5_lon,era5_lat = self.regional_filter(lon_list[i],lat_list[i],qua_list[i],extracted_lon_range,extracted_lat_range)
                if np.sum(region_mask)>0:
                    region_mask_list.append(region_mask)
                    era5_lon_list.append(era5_lon)
                    era5_lat_list.append(era5_lat)
                    sub_domain_file_list.append(full_path_file_list[i])
            if mask_output:
                return(sub_domain_file_list,region_mask_list)
            else:
                return(sub_domain_file_list)
        else:
            print('No .hdf file input, please revise your time period.')
            if mask_output:
                return(sub_domain_file_list,region_mask_list)
            else:
                return(sub_domain_file_list)


    def regional_filter(self, data_lon, data_lat, data_quality=None, extracted_lon_range=[],extracted_lat_range=[], quality_value=0.1):
        import numpy as np
        arr_size=len(data_lon)
        if len(extracted_lon_range)<1 and len(extracted_lat_range)<1:
            lon_s = self.lon_range[0]
            lon_e = self.lon_range[1]
            lat_s = self.lat_range[0]
            lat_e = self.lat_range[1]
        else:
            lon_s = extracted_lon_range[0]
            lon_e = extracted_lon_range[1]
            lat_s = extracted_lat_range[0]
            lat_e = extracted_lat_range[1]

        lon_list = self.fit_era5_lon([data_lon])
        data_lon = lon_list[0]
        data_lat = np.array(data_lat)
        tem_mask = np.zeros((arr_size,1))

        if data_quality == None:
            tem_mask = np.where((data_lon >= lon_s) & (data_lon <= lon_e) & (data_lat >= lat_s) & (data_lat <= lat_e), tem_mask+1, tem_mask)
        else:
            data_quality = np.array(data_quality)
            data_quality = data_quality
            tem_mask = np.where((data_lon >= lon_s) & (data_lon <= lon_e) & (data_lat >= lat_s) & (data_lat <= lat_e) & (data_quality < quality_value), tem_mask+1, tem_mask)

        mask = np.zeros((arr_size,1))
        mask[:,:] = tem_mask
        return(mask,data_lon,data_lat)


    def cross_product_match(self,*lists):
        granule_total = []
        for idx, file_list in enumerate(lists):
            file_list = self.check_list(file_list)
            granule_product = []
            for file_name in file_list:
                split_name = file_name.split('/')[-1]
                granule_product.append(split_name.split('_')[1])
            granule_total.append(granule_product)
            if idx == 1:
                match = sorted(list(set(granule_total[idx-1]) & set(granule_total[idx])))
            elif idx > 1:
                match = sorted(list(set(match) & set(granule_total[idx])))

        match_file_list_total = []
        for idx, file_list in enumerate(lists):
            file_list = self.check_list(file_list)
            match_file_list_product = []
            for i in range(0,len(match)):
                granule_string = '_' + match[i] + '_'
                target_file = list(filter(lambda s: granule_string  in s, file_list))
                match_file_list_product.append(target_file[0])
            match_file_list_total.append(match_file_list_product)
        return(match_file_list_total)

    def plot_track(self,file_list,
                   coast_line_color='olive',lonlat_step=4,font_size=24,
                   loc='left',pad=40, figure_title='CloudSat Track Demo', 
                   prefix='cloudsat_track_demo',
                   figure_name=[],figure_path=[], dpi=300,
                   id_label=True,granule_label=False,date_label=True,
                   utc_label=True, save_fig=True):
        file_list = self.check_list(file_list)
### call outer function
        sub_domain_file_list,region_mask_list \
        = self.sub_domain_check(file_list,mask_output=True)
###
        plot_lon,plot_lat, hdf_date,hdf_id,hdf_granule,\
        region_start_time,region_end_time \
         = self.read_geometric_info(sub_domain_file_list, 
                                    region_mask_list,lonlat_info=True)
### plotting unit
### lon lat info
        lon_s,lon_e,lat_s,lat_e,lon_range,lat_range, \
        lon_step,lat_step = self.plot_lonlat_info(lonlat_step)
### basemap
        ax1,m = self.plot_basemap_unit(lon_s,lon_e,lat_s,lat_e,
                                     lon_range,lat_range,
                                     lon_step,lat_step,
                                     coast_line_color=coast_line_color,
                                     font_size=font_size)
### time zone
        self.plot_timezone_unit(ax1,lon_s,lon_e,lat_s,lat_e,
                                lat_range,utc_label=utc_label)
### plot track main
        self.plot_track_unit(ax1,plot_lon,plot_lat,hdf_date,hdf_id,hdf_granule,
                             lon_range,lat_range,
                             font_size=font_size,granule_label=granule_label,
                             id_label=id_label,date_label=date_label)
### plot title
        title_date =  ''+hdf_date[0].replace('-','/') +' ~ '+hdf_date[-1].replace('-','/')+''
        title = ''+figure_title+'\n'+title_date+''
        self.plot_title_unit(title,loc=loc,pad=pad,font_size=font_size)
### save fig 
        figure_main = ''+hdf_date[0].replace('-','') +'_'+hdf_date[-1].replace('-','')+''
        self.save_fig_unit(figure_main,figure_name=figure_name,
                           prefix=prefix,
                           dpi=dpi, figure_path=figure_path,save_fig=save_fig)        

        if len(file_list) > len(sub_domain_file_list):
            return(sub_domain_file_list)

    def read_vdata(self,full_path_file_list,var_name,region_mask_list,fit_era5_lon=True):
        full_path_file_list = self.check_list(full_path_file_list)
        region_mask_list = self.check_list(region_mask_list)
        var_name = self.check_list(var_name)
        var_list = self.read_ori_vdata(full_path_file_list,var_name)
        if var_name[0] == 'Longitude' and fit_era5_lon:
            var_list = self.fit_era5_lon(var_list)
        region_var_list = self.sub_domain_extract(var_list, region_mask_list)
        return(region_var_list)

    def read_ori_vdata(self,full_path_file_list,var_name):
        from pyhdf import V
        from pyhdf.HDF import HDF, HC
        
        full_path_file_list = self.check_list(full_path_file_list)
        var_name = self.check_list(var_name)
        var_list = []
        print('read variable: '+str(var_name[:])+'')
        for file_name in full_path_file_list:
            reading_vdata = HDF(file_name, HC.READ).vstart()
            vdata_list = reading_vdata.vdatainfo()
            diff_var = []
            for var in var_name:
                for ref in vdata_list:
                    vdata_name = ref[0]
                    target_vdata = var
                    #print(vdata_name)
                    if vdata_name == target_vdata:
                        vdata_length = ref[3]
                        var = reading_vdata.attach(target_vdata)
                        diff_var.append(var.read(vdata_length))
                        var.detach()
                        break
            var_list.append(diff_var[0])
            reading_vdata.end() 
        return(var_list)
 
    def read_sddata(self,full_path_file_list,var_name,region_mask_list):
        import numpy as np
        full_path_file_list = self.check_list(full_path_file_list)
        region_mask_list = self.check_list(region_mask_list)
        var_name = self.check_list(var_name)
        var_list = self.read_ori_sddata(full_path_file_list,var_name)
        region_var_list = self.sub_domain_extract(var_list, region_mask_list)
        return(region_var_list)

    def read_ori_sddata(self,full_path_file_list,var_name):
        from pyhdf.SD  import SD, SDC
        import numpy as np
        full_path_file_list = self.check_list(full_path_file_list)
        var_name = self.check_list(var_name)
        var_list = []
        print('read variable: '+str(var_name[:])+'')
        for file_name in full_path_file_list:
            hdfFile = SD(file_name, SDC.READ)
            diff_var = []
            for var in var_name:
                Var_data = hdfFile.select(var)
                var_data = Var_data[:]
                scale_factor, missing_value = self.cloudsat_var_attribute(var)
                #if mask_missing:
                #    print('test')
                #    print(missing_value[0])
                #    print(np.min(var_data))
                #    var_data  = np.ma.masked_equal(var_data,missing_value[0])
                #print(np.min(var_data))
                var_data = var_data/scale_factor[0]
                diff_var.append(var_data)
            var_list.append(diff_var[0])
            hdfFile.end
        return(var_list)

    def sub_domain_extract(self,var_list,region_mask_list):
        import numpy as np
        var_list = self.check_list(var_list)
        regoion_mask_list = self.check_list(region_mask_list)
        region_var_list = []
        for i in range(0,len(var_list)):
            vertical_len = np.array(var_list[i]).shape[-1]
### prevent no need sub-domain extraction condition
            if len(var_list[i]) > 1:
                if vertical_len > 1:
                    region_var_list.append(np.array(var_list[i])[region_mask_list[i][:,0]>0,:].copy())
                else:
                    region_var_list.append(np.array(var_list[i])[region_mask_list[i][:]>0].copy())
            else:
                region_var_list.append(np.array(var_list[i]))
        return(region_var_list)

    def read_geometric_info(self,sub_domain_file_list,region_mask_list,lonlat_info=False,second_info=False):
        from datetime import datetime, timedelta
        import numpy as np
        sub_domain_file_list = self.check_list(sub_domain_file_list)
        region_mask_list = self.check_list(region_mask_list)
        plot_second = self.read_vdata(sub_domain_file_list,'Profile_time',region_mask_list)
        UTC_start = self.read_vdata(sub_domain_file_list,'UTC_start',region_mask_list)
        if lonlat_info:
            plot_lon = self.read_vdata(sub_domain_file_list,'Longitude',region_mask_list)
            plot_lat = self.read_vdata(sub_domain_file_list,'Latitude',region_mask_list)
        hdf_date = []
        hdf_id = []
        hdf_granule = []
        region_start_time = []
        region_end_time = []
        #plot_second = []
        #plot_mask = []
        for i in range(0,len(sub_domain_file_list)):
### back to date
            split_name = sub_domain_file_list[i].split('/')[-1]
            year = int(split_name[0:4])
            ju = int(split_name[4:7])
    
            base_date = datetime(year, 1, 1)  
            target_date = base_date + timedelta(days=(ju - 1))
            hdf_date.append(str(target_date)[0:10])
            hdf_id.append(i)
            split_name = sub_domain_file_list[i].split('/')[-1]
            hdf_granule.append(split_name.split('_')[1])
### region time
            day_second = UTC_start[i][0] + plot_second[i][0]
            hours, minutes = self.seconds_to_hms(day_second)
            region_start_time.append([int(hours[0]),int(minutes[0])])
            day_second = UTC_start[i][0] + plot_second[i][-1]
            hours, minutes = self.seconds_to_hms(day_second)
            region_end_time.append([int(hours[0]),int(minutes[0])])
        if lonlat_info:
            if second_info:
                return(plot_lon,plot_lat,hdf_date,hdf_id,hdf_granule,region_start_time,region_end_time,UTC_start,plot_second)
            else:
                return(plot_lon,plot_lat,hdf_date,hdf_id,hdf_granule,region_start_time,region_end_time)
        else:
            if second_info:
                return(hdf_date,hdf_id,hdf_granule,region_start_time,region_end_time,UTC_start,plot_second)
            else:
                return(hdf_date,hdf_id,hdf_granule,region_start_time,region_end_time)

    def fit_era5_lon(self,lon_list):
        import numpy as np
        lon_list = self.check_list(lon_list)
        era5_lon_list = []
        for i in range(0,len(lon_list)):
            lon_array = np.array(lon_list[i])
            lon_array = np.where(lon_array >= 0, lon_array, lon_array+360)
            era5_lon_list.append(lon_array)        
        return(era5_lon_list)

    def hdf_information(self,full_path_file_list):
        from pyhdf.SD  import SD, SDC
        from pyhdf import V
        from pyhdf.HDF import HDF, HC
        full_path_file_list = self.check_list(full_path_file_list)
        vdata_name = []
        vdata_len = []
        SD_name = []

        for file_name in full_path_file_list:
            reading_vdata = HDF(file_name, HC.READ).vstart()
            vdata_list = reading_vdata.vdatainfo()
            for ref in vdata_list:
                vdata_name.append(ref[0])
                vdata_len.append(ref[3])
            reading_vdata.end()

            hdfFile = SD(file_name, SDC.READ)
            dsets = hdfFile.datasets()
        for key in dsets.keys():
            SD_name.append(key)
        SD_name.sort()
        hdfFile.end()
        return(vdata_name,vdata_len,SD_name)

    def generate_period(self,year_list, ju_day_list, start_end_hour_list):
        year_list = self.check_list(year_list)
        ju_day_list = self.check_list(ju_day_list)
        start_end_hour_list = self.check_list(start_end_hour_list)
        search_period = []
        for yy in range(0,len(year_list)):
            order = 0
            limit = len(ju_day_list[yy])
            ju_day = ju_day_list[yy]
            hour = start_end_hour_list[yy]
            #print(limit)
            for dd in range(0,len(ju_day)):
                file_d = str(ju_day[dd])
                if ju_day[dd] < 100:
                    file_d = '0' + file_d
                if ju_day[dd] < 10:
                    file_d = '0' + file_d
###  end time
                end_hours = []
                if order == limit-1:
                    if order == 0:
                        if int(hour[0]) == 0 and int(hour[1]) > 23:
                            target_time = [str(year_list[yy]) + file_d]
                            #print(target_time)
                            search_period.extend(target_time)
                        else:
                            end_hours = list(range(int(hour[0]),int(hour[1])))
                    else:
                        if int(hour[1]) > 23:
                            target_time = [str(year_list[yy]) + file_d]
                            #print(target_time)
                            search_period.extend(target_time)
                        else:

                            end_hours = list(range(0,int(hour[1])))          
                    if len(end_hours) > 0:
                        for single_hour in end_hours:
                            file_h = str(single_hour)
                            if single_hour < 10:
                                file_h = '0' + file_h
                            target_time = [str(year_list[yy]) + file_d + file_h]
                            #print(target_time)
                            search_period.extend(target_time)
### start time
                elif order == 0 and int(hour[0]) > 0:
                    end_hours = list(range(int(hour[0]),24))
                    if len(end_hours) > 0:
                        for single_hour in end_hours:
                            file_h = str(single_hour)
                            if single_hour < 10:
                                 file_h = '0' + file_h
                            target_time = [str(year_list[yy]) + file_d + file_h]
                            #print(target_time)
                            search_period.extend(target_time)
### normal condition
                else:
                    target_time = [str(year_list[yy]) + file_d]
                    #print(target_time[0])
                    search_period.extend(target_time)
###  
                order = order + 1 
        return(search_period)
 
    def convert_input_period(self,time_period):
        time_period = self.check_list(time_period)
        year = []
        start_end_hour = []
        year.append(time_period[0][0:4])
        t1 = [time_period[0][8:10],time_period[1][8:10]]
        if year[0] != time_period[1][0:4]:
            year.append(time_period[1][0:4])
        total_period = []
        if len(year) > 1:
            period1 = [time_period[0],year[0]+'12312400']
            period2 = [year[0]+'01010000',time_period[1]]
            total_period.append(period1)
            total_period.append(period2)
        else:
            total_period.append(time_period)
        ju_day = []
        for period in total_period:
            t1_t2 = [period[0][8:10],period[1][8:10]]
            print(period[0],period[1])
            start_end_hour.append(t1_t2)
            ju_day.append(self.julian_time_range(period))
        return(year, ju_day, start_end_hour)

    def julian_time_range(self,time_period):
        from datetime import datetime
        time_period = self.check_list(time_period)
        ju_day = []
        for time in time_period:
            year = int(time[0:4])
            mon = int(time[4:6])
            day = int(time[6:8])
            date = datetime(year, mon, day)
            ju = date.timetuple().tm_yday
            ju_day.append(ju)
        ju_list = list(range(ju_day[0],ju_day[1]+1))
        return(ju_list)
   
    def plot_lonlat_info(self,lonlat_step,extracted_lon_range=[],extracted_lat_range=[]):
        import numpy as np
        if len(extracted_lon_range)<1:
            lon_s = self.lon_range[0]
            lon_e = self.lon_range[1]
        else:
            lon_s = extracted_lon_range[0]
            lon_e = extracted_lon_range[1]

        if  len(extracted_lat_range)<1:
            lat_s = self.lat_range[0]
            lat_e = self.lat_range[1]
        else:
            lat_s = extracted_lat_range[0]
            lat_e = extracted_lat_range[1]

        lon_range = lon_e - lon_s
        lat_range = lat_e - lat_s
        lon_step = np.floor((lon_range)/(lonlat_step-1))
        lat_step = np.floor((lat_range)/(lonlat_step-1))
        return(lon_s,lon_e,lat_s,lat_e,lon_range,lat_range,lon_step,lat_step)

    def seconds_to_hms(self,seconds):
        hours = seconds // 3600 
        minutes = (seconds % 3600) // 60
        return(hours, minutes) 

    def cloudsat_string_info(self):
        color_step = [1,2,3,4,5,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8,1,2,3]
        local_ref_time = ['13','12','11','10','09','08','07',
                          '06','05','04','03','02','01','00',
                          '23','22','21','20','19','18','17',
                          '16','15','14']      
        return(color_step,local_ref_time)
 
    def plot_profile(self,masked_ref=[],masked_cf=[],shading='contourf',
                     x_axis=[],x_step=5,extracted_hei=[],height_range=[0,20],height_step=5,
                     hdf_date=[],hdf_granule=[],
                     region_start_time=[],region_end_time=[],
                     x_label='Latitude',y_label='[km]',
                     figure_title='CloudSat Profile',
                     prefix='cloudsat_profile',figure_name=[],
                     figure_path='cloudsat_fig',dpi=300,save_fig=True):
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
        import numpy as np
        masked_ref = self.check_list(masked_ref)
        masked_cf = self.check_list(masked_cf)
        extracted_hei = self.check_list(extracted_hei)
        x_axis = self.check_list(x_axis)
        hdf_date = self.check_list(hdf_date)
        hdf_granule = self.check_list(hdf_granule)
        region_start_time = self.check_list(region_start_time)
        region_end_time = self.check_list(region_end_time)
        x_s = np.around(x_axis[0][0],decimals=1)
        x_e = np.around(x_axis[0][-1],decimals=1)
        x_range = sorted([x_s,x_e]) 
        x_interval = np.floor((x_range[1] - x_range[0])/(x_step-1))
        
        if x_interval <1:
           x_interval = 1
        light_YlGnBu = mcolors.LinearSegmentedColormap.from_list(
            "custom_YlGnBu", ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#2870c9"], N=256)
        light_YlGnBu.set_under((1, 1, 1, 0))
        fig,ax1 = plt.subplots(1,1,figsize=(20,5),tight_layout=True)
         
        if len(extracted_hei[0].shape) > 1:
            masked_hei = np.ma.masked_equal(extracted_hei[0], -9999)
            reference_hei = np.nanmean(masked_hei,axis=0)/1000
        else:
            masked_hei = np.ma.masked_equal(extracted_hei[0], -9999)
            single_hei = np.zeros((1,125))
            single_hei[0,:] = masked_hei
            reference_hei = np.nanmean(single_hei,axis=0)/1000
        if len(masked_cf)>0:
            if shading == 'pcolormesh':
                cf = plt.pcolormesh(x_axis[0],reference_hei,masked_cf[0].T,
                                    cmap=light_YlGnBu,vmin=30,vmax=100,zorder=2)
            if shading == 'contourf':
                cf = plt.contourf(x_axis[0],reference_hei,masked_cf[0].T,
                                  vmin=30,vmax=100,cmap=light_YlGnBu,extend='min',
                                  levels=np.arange(30,100.05,0.1),zorder=2)
        if shading == 'pcolormesh':
            ref = plt.pcolormesh(x_axis[0],reference_hei,masked_ref[0].T,
                                 cmap='jet',vmin=-30,vmax=16,zorder=2)
        if shading == 'contourf':
            ref = plt.contourf(x_axis[0],reference_hei,masked_ref[0].T,
                               vmin=-30,vmax=16,cmap='jet',extend='both',
                               levels=np.arange(-30,16,0.1),zorder=2)
        plt.xticks(np.arange(x_range[0],x_range[1]+1,x_interval),fontsize=24)
        hei_jump = int(np.floor((height_range[1] - height_range[0])/(height_step-1)))
        if hei_jump == 0:
            hei_jump = 1
        hei_range = list(np.arange(height_range[0],height_range[1]+1,hei_jump))
        hei_ticks = [1]
        hei_ticks.extend(hei_range[1:])
        plt.yticks(hei_ticks,fontsize=24)  

        plt.axis([x_range[0],x_range[1], 
                 height_range[0], height_range[1]])
        plt.xlabel(x_label,fontsize=24)
        plt.ylabel(y_label,fontsize=24)
        plt.grid(zorder=1)
### title unit
        s_hr = str(region_start_time[0][0])
        e_hr = str(region_end_time[0][0])

        if region_start_time[0][0]<10:
           s_hr = '0'+s_hr
        if region_end_time[0][0]<10:
           e_hr = '0'+e_hr
        s_time = ''+s_hr+':'+ str(region_start_time[0][1])+''
        e_time = ''+e_hr+':'+ str(region_end_time[0][1])+'UTC'
        title = ''+figure_title+'\nGranule: '+hdf_granule[0]+'  Cover time: '+s_time+' ~ '+e_time+''
        self.plot_title_unit(title,loc='left',pad=12,font_size=24)
### color bar unit
        cbar_ax = fig.add_axes([0.62, 0.82, 0.15, 0.03])
        c_cf = plt.colorbar(cf,ticks=[30,40,60,80,100],cax=cbar_ax,extend='both',
                            orientation='horizontal', location='top',pad=0.06,
                            fraction=0.05,aspect=16,anchor=(0.95,1.0))
        c_cf.ax.tick_params(labelsize=14)
        c_cf.set_label(label='Cloud fraction [%]', size=12, weight='bold')
        cbar_ax = fig.add_axes([0.82, 0.82, 0.15, 0.03])
        c_ref = plt.colorbar(ref,ticks=[-30,-20,-10,0,10,16],cax=cbar_ax,extend='both',
                             orientation='horizontal', location='top',pad=0.06,
                             fraction=0.05,aspect=16,anchor=(0.75,1.0))
        c_ref.ax.tick_params(labelsize=14)
        c_ref.set_label(label='Reflectivity [dBZ]', size=12, weight='bold')
### save fig unit
        fig_s_time = ''+s_hr+''+ str(region_start_time[0][1])+''
        fig_e_time = ''+e_hr+''+ str(region_end_time[0][1])+''
        figure_main = ''+hdf_date[0].replace('-','') +'_'+fig_s_time+'_'+fig_e_time+'_'+hdf_granule[0]+''
        self.save_fig_unit(figure_main,figure_name=[],
                           prefix=prefix, dpi=dpi, 
                           figure_path=figure_path,save_fig=save_fig)

    def plot_track_w_rgb(self,file_list=[],
                         rgb_array=[],plotting_lon_list=[],plotting_lat_list=[],
                         extracted_lon=[],extracted_lat=[],
                         extracted_hdf_date=[],extracted_hdf_id=[],extracted_hdf_granule=[],
                         extracted_region_start_time=[],
                         extracted_region_end_time=[],
                         extracted_lon_range=[],extracted_lat_range=[],
                         coast_line_color='gold',
                         lonlat_c='k',lonlat_width=0.01,lonlat_order=1,
                         lonlat_step=4,font_size=24,
                         loc='left',pad=12,
                         figure_title='CloudSat Track',rgb_product='',rgb_time='',
                         prefix='cloudsat_track_w_truecolor',figure_name=[],
                         dpi=300, figure_path='cloudsat_fig',
                         granule_label=False,id_label=False,
                         date_label=False,extracted_time=False,save_fig=True):
        import matplotlib.pyplot as plt
        import numpy as np
        file_list = self.check_list(file_list)
        rgb_array = self.check_list(rgb_array)
        plotting_lon_list = self.check_list(plotting_lon_list)
        plotting_lat_list = self.check_list(plotting_lat_list)
        
        ### lon lat info
        lon_s,lon_e,lat_s,lat_e,lon_range,lat_range, \
        lon_step,lat_step = self.plot_lonlat_info(lonlat_step,
                                                  extracted_lon_range,
                                                  extracted_lat_range)
        ### basemap
        ax1,m = self.plot_basemap_unit(lon_s,lon_e,lat_s,lat_e,
                                       lon_range,lat_range,
                                       lon_step,lat_step,
                                       coast_line_color=coast_line_color,
                                       lonlat_c=lonlat_c,lonlat_width=lonlat_width,
                                       lonlat_order=lonlat_order,
                                       font_size=font_size)
        fig_num = 0
        xi, yi = np.meshgrid(plotting_lon_list[0],plotting_lat_list[0])
        m.pcolormesh(xi,yi,rgb_array[fig_num])

        sub_domain_file_list,region_mask_list \
        = self.sub_domain_check(file_list,mask_output=True)
###
        plot_lon,plot_lat, hdf_date,hdf_id,hdf_granule,\
        region_start_time,region_end_time \
         = self.read_geometric_info(sub_domain_file_list,
                                    region_mask_list,lonlat_info=True)
### plot track main
        self.plot_track_unit(ax1,plot_lon,plot_lat,hdf_date,hdf_id,hdf_granule,
                             lon_range,lat_range,
                             font_size=font_size,granule_label=granule_label,
                             id_label=id_label,date_label=date_label)
### plot extracted track
        if len(extracted_lon) > 0:
            self.plot_track_unit(ax1,extracted_lon,extracted_lat,
                                 extracted_hdf_date,extracted_hdf_id,extracted_hdf_granule,
                                 lon_range,lat_range,line_color='mediumblue',
                                 font_size=font_size,granule_label=False,
                                 id_label=False,date_label=False)
            if extracted_time:
                for i in range(0,len(extracted_lon)):
                    s_hr = str(extracted_region_start_time[i][0])
                    e_hr = str(extracted_region_end_time[i][0])
                    if region_start_time[i][0]<10:
                        s_hr = '0'+s_hr
                    if region_end_time[i][0]<10:
                        e_hr = '0'+e_hr
                    s_time = ''+s_hr+':'+ str(extracted_region_start_time[0][1])+'UTC'
                    e_time = ''+e_hr+':'+ str(extracted_region_end_time[0][1])+'UTC'
                    ax1.text(extracted_lon[0][0],extracted_lat[0][0],s_time,c='teal',
                             fontsize=font_size, fontweight='bold',
                             va='top', ha='center',
                             bbox=dict(facecolor='ghostwhite', 
                             edgecolor='midnightblue',
                             boxstyle='round,pad=0.1'),
                             zorder=5)
                    ax1.text(extracted_lon[0][-1],extracted_lat[0][-1],e_time,c='teal',
                             fontsize=font_size, fontweight='bold',
                             va='bottom', ha='center',
                             bbox=dict(facecolor='ghostwhite',
                             edgecolor='midnightblue',
                             boxstyle='round,pad=0.1'),
                             zorder=5)
###
### plot title
        title_date =  ''+hdf_date[0].replace('-','/') +' ~ '+hdf_date[-1].replace('-','/')+''
        title = ''+figure_title+' \n'+title_date+'\n'+rgb_product+' '+rgb_time+''
        self.plot_title_unit(title,loc=loc,pad=pad,font_size=font_size)
### save fig
        figure_main = ''+hdf_date[0].replace('-','') +'_'+hdf_granule[0]+''
        self.save_fig_unit(figure_main,figure_name=figure_name,
                           prefix=prefix,
                           dpi=dpi, figure_path=figure_path,save_fig=save_fig)


    def plot_basemap_unit(self,lon_s,lon_e,lat_s,lat_e,lon_range,lat_range,lon_step,lat_step,coast_line_color='olive',lonlat_c='k',lonlat_width=0.01,lonlat_order=1,font_size=24):
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.basemap import Basemap
        if lon_range > lat_range:
            fig,ax1 = plt.subplots(1,1,figsize=(13*(lon_range/lat_range),13.3),tight_layout=True)
        else:
            fig,ax1 = plt.subplots(1,1,figsize=(13,13.4*(lat_range/lon_range)),tight_layout=True)
        m = Basemap(llcrnrlon=lon_s, urcrnrlon=lon_e, llcrnrlat=lat_s, urcrnrlat=lat_e,resolution='i')
        m.drawparallels(np.arange(lat_s, lat_e+1, lat_step), 
                        labels=[1, 0, 0, 0], linewidth=lonlat_width, color=lonlat_c, 
                        fontsize=font_size-2,zorder=lonlat_order)
        m.drawmeridians(np.arange(lon_s, lon_e+1, lon_step), 
                        labels=[0, 0, 0, 1], linewidth=lonlat_width, color=lonlat_c, 
                        fontsize=font_size-2,zorder=lonlat_order)
        m.drawcoastlines(linewidth=1.3,color=coast_line_color,zorder=3)
        return(ax1,m)

    def plot_timezone_unit(self,ax1,lon_s,lon_e,lat_s,lat_e,lat_range,font_size=24,utc_label=True):
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon
        import matplotlib.cm as cm

### time zone
        lon_min = np.arange(-7.5,338,15)
        lon_max = np.arange(7.5,353,15)
        lat_min, lat_max = lat_s, lat_e
        color_step, local_ref_time = self.cloudsat_string_info()
        cmap = cm.get_cmap('Blues_r', len(lon_min)*3)
        zone_num = int(lon_e/15)+1
        if zone_num >24:
           zone_num = 24
        for j in range(int(lon_s/15),zone_num):
            polygon = [(lon_min[j], -90), (lon_max[j], -90), (lon_max[j], 90), (lon_min[j], 90)]
            color = cmap(color_step[j]*3 / len(lon_min))
            poly_map = Polygon(polygon, edgecolor='thistle', facecolor=color, alpha=1, linewidth=2)
            ax1.add_patch(poly_map)
            utc_pos = (lon_max[j] + lon_min[j])/2
            if utc_pos < lon_s:
                utc_pos = lon_s
            if utc_pos > lon_e:
                utc_pos = lon_e
            if utc_label:
                plt.text(utc_pos,lat_max+(lat_range/180),''+local_ref_time[j]+'UTC',c='teal',
                         fontsize=font_size-2, fontweight='bold',
                         va='bottom',ha='center',
                         bbox=dict(facecolor='ghostwhite', edgecolor='indigo', boxstyle='round,pad=0.1'),zorder=6)

    def plot_track_unit(self,ax1,plot_lon,plot_lat,hdf_date,hdf_id,hdf_granule,lon_range,lat_range,line_color='orangered',font_size=24,id_label=True,granule_label=False,date_label=True):
        import numpy as np
        import matplotlib.pyplot as plt
        from mpl_toolkits.basemap import Basemap

### illustration
        if lon_range > lat_range:
            y_pos=0.075
            x_pos=0.033/(lon_range/lat_range)
        else:
            y_pos=0.075/(lat_range/lon_range)
            x_pos=0.033

        for i in range(0,len(plot_lon)):
            ax1.scatter(plot_lon[i],plot_lat[i],12,c=line_color,zorder=4)
            id_pos = int(len(plot_lon[i])/2)
            if id_label:
                if granule_label:
                    ax1.text(plot_lon[i][id_pos],plot_lat[i][id_pos],
                             ''+str(int(hdf_granule[i]))+'',c='darkorange',
                             fontsize=font_size-4, fontweight='bold',
                             ha='center',
                             bbox=dict(facecolor='ghostwhite', edgecolor='crimson', boxstyle='round,pad=0.1'),zorder=5)
                else:
                    ax1.text(plot_lon[i][id_pos],plot_lat[i][id_pos],
                             ''+str(hdf_id[i])+'',c='darkorange',
                             fontsize=font_size-4, fontweight='bold',
                             ha='center',
                             bbox=dict(facecolor='ghostwhite', edgecolor='crimson', boxstyle='round,pad=0.1'),zorder=5)
#               plt.text(np.mean(plot_lon[i]),np.mean(plot_lat[i]),''+str(i)+'',c='darkorange',
#                        fontsize=font_size-4, fontweight='bold',
#                        bbox=dict(facecolor='ghostwhite', edgecolor='crimson', boxstyle='round,pad=0.1'),zorder=5)
            if date_label:
                date_pos = np.unravel_index(np.argmin(plot_lat[i]), plot_lat[i].shape)
                ax1.text(plot_lon[i][date_pos],plot_lat[i][date_pos],
                         ''+str(int(hdf_date[i][8:10]))+'',c='Navy',
                         fontsize=font_size-6, fontweight='bold',
                         va='top', ha='left',
                         bbox=dict(facecolor='snow', edgecolor='khaki',
                         boxstyle='round,pad=0.1'),zorder=5)
#        y_pos=0.075
#        x_pos=0.033/(lon_range/lat_range)
        if date_label:
            ax1.text(0.85,1+y_pos,'1',c='Navy',
                     fontsize=font_size, fontweight='bold',
                     va='center_baseline', ha='left',
                     bbox=dict(facecolor='snow', edgecolor='khaki', boxstyle='round,pad=0.1'),
                     transform=ax1.transAxes,zorder=5)
            ax1.text(0.85+x_pos,1.003+y_pos,'Date',
                     fontsize=font_size-2,
                     va='top', ha='left',
                     transform=ax1.transAxes,zorder=5)
        if id_label:
            ax1.text(0.63,1+y_pos,'0',c='darkorange',
                     fontsize=font_size, fontweight='bold',
                     va='center_baseline', ha='left',
                     bbox=dict(facecolor='ghostwhite', edgecolor='crimson', boxstyle='round,pad=0.1'),
                     transform=ax1.transAxes,zorder=5)
            ax1.text(0.63+x_pos,1.003+y_pos,'hdf ID',
                     fontsize=font_size-2,
                     va='top', ha='left',
                     transform=ax1.transAxes,zorder=5)

    def plot_title_unit(self,title,loc='left',pad=40,font_size=24):
### figure info
        import matplotlib.pyplot as plt
        plt.title(title,loc=loc,fontsize=font_size,pad=pad)

    def save_fig_unit(self,figure_main,figure_name=[],prefix='cloudsat_track_demo',
                      dpi=300, figure_path=[],save_fig=True):
        from pathlib import Path
        import matplotlib.pyplot as plt
        if save_fig:
            if figure_path == None or figure_path == []:
                figure_path = ''+str(self.work_path)+'/'
            else:
                Path(figure_path).mkdir(parents=True, exist_ok=True)
                figure_path = ''+str(figure_path)+'/'

            if len(figure_name)>0:
                figure_main = ''+figure_name+'_'+figure_main+''
            plt.savefig(''+figure_path+''+prefix+'_'+figure_main+'.png',dpi=dpi)
    """
    var information
    """

    def cloudsat_var_attribute(self,var_name):
        var_name = self.check_list(var_name)
        scale_factor = []
        missing_value = []
        for var in var_name:
            var = var.replace('-', '_')
            if var == 'Radar_Reflectivity' or var == 'Gaseous_Attenuation':
                scale_factor.append(100)
            else:
                scale_factor.append(1)
            method = getattr(self, var)
            missing = method()
            missing_value.append(missing)
        return(scale_factor,missing_value)

    def CPR_Cloud_mask(self):
        missing_value = -9
        return(missing_value)
    def Radar_Reflectivity(self):
        missing_value = -88.88
        return(missing_value)
    def Gaseous_Attenuation(self):
        missing_value = -99.99
        return(missing_value)
    def CloudFraction(self):
        missing_value = -9
        return(missing_value)
    def Profile_time(self):
        missing_value = []
        return(missing_value)
    def UTC_start(self):
        missing_value = []
        return(missing_value)
    def TAI_start(self):
        missing_value = []
        return(missing_value)
    def Latitude(self):
        missing_value = []
        return(missing_value)
    def Longitude(self):
        missing_value = []
        return(missing_value)
    def Height(self):
        missing_value = -9999
        return(missing_value)
    def Range_to_intercept(self):
        missing_value = []
        return(missing_value)
    def DEM_elevation(self):
        missing_value = 9999
        return(missing_value)
    def Vertical_binsize(self):
        missing_value = -9999.0
        return(missing_value)
    def Pitch_offset(self):
        missing_value = []
        return(missing_value)
    def Roll_offset(self):
        missing_value = []
        return(missing_value)
    def Data_quality(self):
        missing_value = []
        return(missing_value)
    def Data_status(self):
        missing_value = []
        return(missing_value)
    def Data_targetID(self):
        missing_value = []
        return(missing_value)
    def RayStatus_validity(self):
        missing_value = []
        return(missing_value)
    def SurfaceHeightBin(self):
        missing_value = -1
        return(missing_value)
    def SurfaceHeightBin_fraction(self):
        missing_value = 0.0
        return(missing_value)
    def Sigma_Zero(self):
        missing_value = -9999
        return(missing_value)
    def MODIS_cloud_flag(self):
        missing_value = 99
        return(missing_value)
    def MODIS_Cloud_Fraction(self):
        missing_value = -99
        return(missing_value)
    def MODIS_scene_char(self):
        missing_value = -9
        return(missing_value)
    def MODIS_scene_var(self):
        missing_value = -9
        return(missing_value)
    def CPR_Echo_Top(self):
        missing_value = -9
        return(missing_value)
    def sem_NoiseFloor(self):
        missing_value = 0.0
        return(missing_value)
    def sem_NoiseFloorVar(self):
        missing_value = 0.0
        return(missing_value)
    def sem_NoiseGate(self):
        missing_value = 0
        return(missing_value)
    def Navigation_land_sea_flag(self):
        missing_value = []
        return(missing_value)
    def Clutter_reduction_flag(self):
        missing_value = []
        return(missing_value)
    def sem_MDSignal(self):
        missing_value = 9999.0
        return(missing_value)
    def CloudFraction(self):
        missing_value = -9
        return(missing_value)
    def VFMHistogram(self):
        missing_value = -9
        return(missing_value)
    def UncertaintyCF(self):
        missing_value = -9
        return(missing_value)
    def LayerBase(self):
        missing_value = -99
        return(missing_value)
    def LayerTop(self):
        missing_value = -99
        return(missing_value)
    def FlagBase(self):
        missing_value = -9
        return(missing_value)
    def FlagTop(self):
        missing_value = -9
        return(missing_value)
    def DistanceAvg(self):
        missing_value = -99
        return(missing_value)
    def NumLidar(self):
        missing_value = -9
        return(missing_value)
    def CloudLayers(self):
        missing_value = -9
        return(missing_value)





    """
    not on current to do list
    """
    def download(self):
        pass

