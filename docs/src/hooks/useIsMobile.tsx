import { useState, useEffect, useLayoutEffect } from "react";

function useIsMobile(maxWidth = 1000) {
    const [mobile, setMobile] = useState(false);

    function handleWindowSizeChange() {
        setMobile(matchMedia(`(max-width: ${maxWidth}px)`).matches);
    }
    useLayoutEffect(() => {
        handleWindowSizeChange();
        window.addEventListener('resize', handleWindowSizeChange);
        return () => {
            window.removeEventListener('resize', handleWindowSizeChange);
        }
    }, []);

    return mobile;
}

export default useIsMobile;