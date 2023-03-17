import React from "react";
import Marquee from "react-fast-marquee";
import { Center } from "@chakra-ui/react";

function MarqueeText({ songState }) {
    return (
      <Center>
        <Marquee
          speed={60}
          gradientWidth={50}
          style={{
            width: "400px",
          }}
        >
          {songState}
        </Marquee>
      </Center>
    );
  }

export default MarqueeText;