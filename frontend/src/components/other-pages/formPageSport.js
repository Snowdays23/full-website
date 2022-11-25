import * as React from 'react';
import Separator from '../subcomponents/separator';
import logoSD23 from '../../assets/img/Logo_SD_23.svg';
import "../../assets/css/style.css";
import "../../assets/css/bootstrap.min.css";  
import "../../assets/css/other-pages-css/styleFormPage.css";
import Snowfall from 'react-snowfall';
import TextField from '@mui/material/TextField';
import { Checkbox } from '@mui/material/';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DesktopDatePicker } from '@mui/x-date-pickers/DesktopDatePicker';
import dayjs, { Dayjs } from 'dayjs';
import MenuItem from '@mui/material/MenuItem';
import { createTheme, ThemeProvider } from '@mui/material/styles';

export const FormPageSport = () => {

    // const theme = createTheme({
    //     components: {
    //       MuiTextField: {
    //         styleOverrides: {
    //           root: ({ ownerState }) => ({
    //             ...(ownerState.variant === 'filled' &&
    //               ownerState.color === 'primary' && {
    //                 backgroundColor: '#fff'
    //               }),
    //           }),
    //         },
    //       },
    //     },
    //   });
    
    // const [value, setValue] = React.useState();
    
    // const handleChange = (newValue) => {
    //     setValue(newValue);
    // };

    const [gear, setGear] = React.useState('');

    const handleChangeGear = (event) => {
        setGear(event.target.value);
    };

    const gears = [
        {
          value: 'Snowboard',
          label: 'Snowboard',
        },
        {
          value: 'Snowboard_Boots',
          label: "Snowboard Boots",
        },
        {
          value: 'Skii',
          label: 'Skii',
        },
        {
          value: 'Skii_Boots',
          label: "Skii Boots",
        },
        {
          value: 'Skii_Poles',
          label: "Skii Poles",
        },
        {
          value: 'Helmet',
          label: "Helmet",
        }
      ];

      const [size, setSize] = React.useState('');

    const handleChangeSize = (event) => {
        setSize(event.target.value);
    };

    const sizes = [
        {
          value: 'XS',
          label: 'XS',
        },
        {
          value: 'S',
          label: "S",
        },
        {
          value: 'M',
          label: 'M',
        },
        {
          value: 'L',
          label: "L",
        },
        {
          value: 'XL',
          label: "XL",
        }
      ];


    
        return (
            <div>
                {/* <Separator number={4} ></Separator> */}
                <div className='row justify-content-center'>
                    <div className='col-12 col-sm-7 col-lg-5' style={{position: "relative", right: -20 }}>
                        <div style={{backgroundColor: "white", height: '100%', width: '90%'}}>
                            <label> Want to ski / do snowboard <Checkbox defaultChecked /></label>
                        </div>
                    </div>
                </div>

                

                <Separator number = {2} />

                <div className='row justify-content-center'>
                    <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                        <TextField id="filled-basic" label="Height" variant="filled" style={{width:'90%'}} />
                    </div>
                    <div className="d-none d-lg-block col-lg-1"></div>
                    <div className='col-6 col-lg-5' style={{position: "relative", right: 13 }}>
                        <TextField id="filled-basic" label="Weight" variant="filled" style={{width:'90%'}} />
                    </div>
                </div>

                <Separator number = {2} />

                <div className='row justify-content-center'>
                    <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                        <TextField id="filled-basic" label="Shoe Size" variant="filled" style={{width:'90%'}} />
                    </div>
                    <div className="d-none d-lg-block col-lg-1"></div>
                    <div className='col-6 col-lg-5' style={{position: "relative", right: 13}} >
                        <TextField
                        id="filled-select-helmet-size"
                        select
                        label="Helmet Size"
                        value={size}
                        onChange={handleChangeSize}
                        variant="filled"
                        style={{width:'90%'}}
                        >
                            {sizes.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                {option.label}
                                </MenuItem>
                            ))}
                        </TextField>                                   
                    </div>
                </div>

                <Separator number = {2} />

                <div className='row justify-content-center'>
                    <div className='col-12 col-sm-7 col-lg-5' style={{position: "relative", right: -20 }}>
                        <div style={{backgroundColor: "white", height: '100%', width: '90%'}}>
                            <label> Day 1 <Checkbox defaultChecked /></label>
                        </div>
                    </div>
                </div>

                <Separator number = {2} />

                <div className='row justify-content-center'>
                    <div className='col-6 col-lg-5' style={{position: "relative", right: 13}} >
                        <TextField
                        id="filled-select-gear"
                        select
                        label="Gear"
                        value={gear}
                        onChange={handleChangeGear}
                        variant="filled"
                        style={{width:'90%'}}
                        >
                            {gears.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                {option.label}
                                </MenuItem>
                            ))}
                        </TextField>                                   
                    </div>
                </div>

            </div>
            
        );
    
}