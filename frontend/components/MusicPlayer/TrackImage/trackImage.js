import { Center, Image } from "@chakra-ui/react";
import React from "react";

function TrackImage({ thumbnailUrl }) {
    return (
      <Center>
        {thumbnailUrl && (
          <Image
            src={thumbnailUrl}
            fallbackSrc="/images/default2.png"
            borderRadius='20px' 
            objectFit="cover"
            objectPosition="center"
            height="500px"
            width="500px"
          /> 
        )}
      </Center>
    );
  }

export default TrackImage;