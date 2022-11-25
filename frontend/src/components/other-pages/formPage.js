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
import { FormPageSport } from './formPageSport';

export const FormPage = () => {

    const theme = createTheme({
        components: {
          MuiTextField: {
            styleOverrides: {
              root: ({ ownerState }) => ({
                ...(ownerState.variant === 'filled' &&
                  ownerState.color === 'primary' && {
                    backgroundColor: '#fff'
                  }),
              }),
            },
          },
        },
      });
    
    const [value, setValue] = React.useState();
    
    const handleChange = (newValue) => {
        setValue(newValue);
    };

    const [gender, setGender] = React.useState('');

    const handleChangeGender = (event) => {
        setGender(event.target.value);
    };

    const genders = [
        {
          value: 'M',
          label: 'Male',
        },
        {
          value: 'F',
          label: 'Female',
        },
        {
          value: 'N',
          label: "Don't want to specify",
        }
      ];
    
        return (

            <div className = "wrapper-outside  ">


                    

                <div className='absolute overlay-1' >

                    <div className='d-xs-block d-lg-none'>
                        <Snowfall  snowflakeCount={80}/>    
                    </div>

                    <div className='d-none d-lg-block'>
                        <Snowfall  snowflakeCount={180}/>   
                    </div>
                    

                    <div className='row justify-content-center'>

                        <div className='col-12 mt-5'>
                            <img src={logoSD23}  id = "main-logo" className='white-shadow-stronger'  alt="Snowdays23 logo: blue snowflake with writing: SNOWDAYS"/>
                        </div>

                    </div>

                    <Separator number={8} ></Separator>

                    <div className='row justify-content-center'>

                        <div className='col-10 '>
                            <h2 className='text-black font-josefin subtitle'>READY TO JOIN US?</h2>
                        </div>

                        <div className="w-100"></div>

                        <div className='col-10'>
                            <h2 className='text-black font-josefin normal-text'>fill in your details</h2>
                        </div>

                        <Separator number={8} ></Separator>

                        <ThemeProvider theme={theme} >

                            <div className='col-11 col-lg-8 '>
                                
                                <div id='form' className='p-1 '>
                                    <Separator number={4} ></Separator>
                                    <div className='row justify-content-center'>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                                            <TextField id="filled-basic" label="Name" variant="filled" style={{width:'90%'}} />
                                        </div>
                                        <div className="d-none d-lg-block col-lg-1"></div>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: 13 }}>
                                            <TextField id="filled-basic" label="Last Name" variant="filled" style={{width:'90%'}} />
                                        </div>
                                    </div>
                                    <Separator number={2} ></Separator>
                                    <div className='row justify-content-center'>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                                            <TextField id="filled-basic" label="Email" variant="filled" style={{width:'90%'}} />
                                        </div>
                                        <div className="d-none d-lg-block col-lg-1"></div>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: 13}} >
                                            {/* <TextField id="filled-basic" label="Date of Birth" variant="filled" style={{width:'90%'}} /> */}
                                            <LocalizationProvider dateAdapter={AdapterDayjs } >
                                                <DesktopDatePicker
                                                label="Date Birth"
                                                inputFormat="DD/MM/YYYY"
                                                value={value}
                                                onChange={handleChange}
                                                renderInput={(params) => <TextField {...params} style={{width:'90%'}} id="filled-basic" variant="filled" />}
                                                />
                                            </LocalizationProvider>                                        
                                        </div>
                                    </div>
                                    <Separator number={2} ></Separator>
                                    <div className='row justify-content-center'>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                                            <TextField id="filled-basic" label="Student Nr" variant="filled" style={{width:'90%'}} />
                                        </div>
                                        <div className="d-none d-lg-block col-lg-1"></div>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: 13}} >
                                            <TextField
                                            id="filled-select-gender"
                                            select
                                            label="Gender"
                                            value={gender}
                                            onChange={handleChangeGender}
                                            variant="filled"
                                            style={{width:'90%'}}
                                            >
                                                {genders.map((option) => (
                                                    <MenuItem key={option.value} value={option.value}>
                                                    {option.label}
                                                    </MenuItem>
                                                ))}
                                            </TextField>                                   
                                        </div>
                                    </div>
                                    <Separator number={2} ></Separator>
                                    <div className='row justify-content-center'>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: -13}}>
                                            <TextField id="filled-basic" label="University" variant="filled" style={{width:'90%'}} />
                                        </div>
                                        <div className="d-none d-lg-block col-lg-1"></div>
                                        <div className='col-6 col-lg-5' style={{position: "relative", right: 13}}>
                                            <TextField id="filled-basic" label="Phone Number" variant="filled" style={{width:'90%'}} />
                                        </div>
                                    </div>
                                    <Separator number={2} ></Separator>
                                    <div className='row justify-content-center'>
                                        <div className='col-12 col-sm-7 col-lg-5' style={{position: "relative", right: -20 }}>
                                            <div style={{backgroundColor: "white", height: '100%', width: '90%'}}>
                                                <label>Need Accomodation <Checkbox defaultChecked /></label>
                                            </div>
                                        </div>
                                    </div>

                                    <Separator number={5} ></Separator>

                                    <FormPageSport />
                                </div>
                            </div>
                        </ThemeProvider>

                        <Separator number={8} ></Separator>

                        

                    </div>

                </div>

                

                
                

            </div>
            
            
        );
    
}