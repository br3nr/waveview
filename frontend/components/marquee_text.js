import React from "react";
import Marquee from "react-fast-marquee";
import { Center } from "@chakra-ui/react";

function MarqueeText({ songState }) {
    return (
      <Center>
        <Marquee
          speed={30}
          gradientColor="#1A202C"
          gradientWidth={50}
          style={{
            width: "450px",
          }}
        >
          {songState}
        </Marquee>
      </Center>
    );
  }

export default MarqueeText;