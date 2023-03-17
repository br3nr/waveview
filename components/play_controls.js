import { Center, Button, Icon } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward } from "react-icons/fa";
import React from "react";
import { useState } from "react";

function PlayControls() {
    const [buttonState, setButtonState] = useState("pause");

    async function handleClick() {
        if (buttonState == "pause") {
            const response = await fetch('/pause');
        } else {
            const response = await fetch('/resume');
        }
        setButtonState(buttonState === "play" ? "pause" : "play");
    }

    async function skipSong() {
        await fetch('/skip');
    }

    return (
        <Center>
            <Button onClick={handleClick}>
                {buttonState === "play" ? (
                    <Icon as={FaPlay} />
                ) : (
                    <Icon as={FaPause} />
                )}
            </Button>
            <Button onClick={skipSong}>
                <Icon as={FaStepForward} />
            </Button>
        </Center>
    );
}

export default PlayControls;