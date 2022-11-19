import React, { Component } from 'react';
import Separator from '../subcomponents/separator';
import logoSD23 from '../../assets/img/Logo_SD_23.svg';
import "../../assets/css/style.css";
import "../../assets/css/bootstrap.min.css";  
import "../../assets/css/other-pages-css/styleFormPage.css";
import Snowfall from 'react-snowfall';

export const FormPage = () => {
    
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

                        <div className='col-10 col-lg-8 '>
                            <div id='form'>
                            </div>
                        </div>

                        <Separator number={8} ></Separator>

                    </div>

                </div>

                

                
                

            </div>
            
            
        );
    
}