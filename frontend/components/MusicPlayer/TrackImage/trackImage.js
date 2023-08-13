import { Center, Image, Box } from "@chakra-ui/react";
import React from "react";
import { useState, useEffect } from "react";

function TrackImage({ thumbnailUrl }) {
  const [size, setSize] = useState(0);

  // Ensures that the image is a square, and based on 80%
  // of the container.
  useEffect(() => {
    const container = document.getElementById("container");
    const containerWidth = container.offsetWidth;
    setSize(containerWidth);
  }, []);

  return (
    <Center>
      <Box id="container" width="80%" position="relative">
        <Box
          top="0"
          left="0"
          width="100%"
          paddingBottom="100%"
        >
          <Image
            src={thumbnailUrl}
            objectFit="cover"
            position="absolute"
            top="0"
            left="0"
            width="100%"
            height="100%"
            borderRadius="20px"
            backgroundColor="primary.900"
          />
        </Box>
      </Box>
    </Center>
  );
}

export default TrackImage;