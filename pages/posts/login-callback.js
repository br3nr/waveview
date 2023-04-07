import { useState, useEffect } from "react";
import { useToast } from "@chakra-ui/react";
import Cookies from "js-cookie";

function LoginCallback() {
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const accessToken = Cookies.get("access_token");
    if (accessToken) {
      // Do something with the access token
      console.log(accessToken);
    } else {
      toast({
        title: "Error",
        description: "Access token not found",
        status: "error",
        duration: 9000,
        isClosable: true,
      });
    }
    setLoading(false);
  }, []);

  return (
    <div>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <p>Access token: {Cookies.get("current_user")}</p>
      )}
    </div>
  );
}

export default LoginCallback;
