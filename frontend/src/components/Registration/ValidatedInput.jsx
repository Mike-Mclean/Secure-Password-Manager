import React, { useState, useEffect } from 'react';

export default function ValidatedInput({ 
  name, 
  type = "text", 
  placeholder, 
  value, 
  onChange, 
  onValidationChange, // callback to propogate the status back to parent. forward ref doesn't work 
  minLength = 100,
  apiEndpoint = "/api/accounts/check-user/",
  label 
}) {
  const [status, setStatus] = useState({
    isChecking: false,
    available: null,
    message: ''
  });

  // Notify parent when validation status changes
  useEffect(() => {
    if (onValidationChange) {
      onValidationChange(name, status);
    }
  }, [status, name, onValidationChange]);

  useEffect(() => {
    const checkAvailability = async () => {
      if (!value || value.length < minLength) {
        setStatus({ isChecking: false, available: null, message: '' });
        return;
      }

      setStatus({ isChecking: true, available: null, message: 'Checking availability...' });

      try {
        const response = await fetch(`${apiEndpoint}?field=${name}&value=${encodeURIComponent(value)}`);
        const data = await response.json();

        if (response.ok) {
          setStatus({
            isChecking: false,
            available: data.available,
            message: data.available ? `${value} is available` : `${value} is already taken`
          });
        } else {
          setStatus({
            isChecking: false,
            available: false,
            message: `Error checking ${name}`
          });
        }
      } catch (error) {
        setStatus({
          isChecking: false,
          available: false,
          message: `Error: ${error.message}`
        });
      }
    };

    const timeoutId = setTimeout(checkAvailability, 500);
    return () => clearTimeout(timeoutId);
  }, [value, name, minLength, apiEndpoint]);

  return (
    <>
      <label>{label}:</label>
      <input 
        type={type}
        name={name}
        value={value || ""}
        onChange={onChange}
        placeholder={placeholder}
      />
      {status.message && (
        <div style={{ color: status.available ? 'green' : 'red' }}>
          {status.isChecking && <span>... </span>}
          {status.message}
        </div>
      )}
    </>
  );
}