import React from 'react';

const CSRFToken = () => {
    const csrftoken = document.cookie.split('; ')
        .map(cookie => cookie.split('='))
        .find(([key]) => key === "csrftoken")?.[1] || null;;
    return (
        { "X-CSRFToken": csrftoken }
    );
};
export default CSRFToken;