import React, { useState } from 'react';
import ValidatedInput from './ValidatedInput';

export default function RegistrationForm(props) {
  const [inputs, setInputs] = useState({
    email: '',
    password: ''
  });
  
  const [validationStatus, setValidationStatus] = useState({
    email: { isValid: null },
    password: { isValid: null }
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setInputs(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleValidationChange = (fieldName, status) => {
    setValidationStatus(prev => ({
      ...prev,
      [fieldName]: status
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // if (validationStatus.email.isValid !== true || validationStatus.password.isValid !== true) {
    //   console.log('invalid inputs');
    //   return;
    // }

    console.log('Form inputs:', inputs);
    
    try {
      const response = await fetch(`/api/accounts/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(inputs)
      });
      const data = await response.json();
      console.log('Response:', data);
      // TODO: handle redirect or whatever after registration
      props.processData(inputs);
    } catch (error) {
      console.error('Registration error:', error);
    }
  };

  return (
    <div>
      
      <form onSubmit={handleSubmit}>
        <ValidatedInput
          name="email"
          type="email"
          label="Email"
          placeholder="Enter your email"
          value={inputs.email}
          onChange={handleChange}
          onValidationChange={handleValidationChange}
        />

        <ValidatedInput
          name="password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          value={inputs.password}
          onChange={handleChange}
          onValidationChange={handleValidationChange}
        />

        <button 
          type="submit"
          disabled={
            validationStatus.email.available === false || 
            validationStatus.password.available === false
          }
        >
          Submit
        </button>
      </form>
    </div>
  );
}