import { Box, Center, Button, Icon, useColorMode } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward, FaLightbulb } from "react-icons/fa";
import React from "react";
import { useState } from "react";
import { Input, Form } from "@chakra-ui/react";

function PlayControls() {
    const [buttonState, setButtonState] = useState("pause");
    const [spinning, setSpinning] = useState(0);
    const { colorMode, toggleColorMode } = useColorMode()
		const [value, setValue] = React.useState('')
  	const handleChange = (event) => setValue(event.target.value)


    async function handleRestartClick() {
        setSpinning(1);
        await fetch('/restart');
    };

    const handleKeyPress = async (event) => {
        if (event.key === "Enter") {
						setValue("")
            const url = `http://localhost:5090/play_song/${value}`;
            await fetch(url);
            // Do something, e.g. submit a query
            console.log("Enter key pressed!");
						console.log(value)
        }
    };

    async function handleClick() {
        setButtonState(buttonState === "play" ? "pause" : "play");

        if (buttonState == "pause") {
            const response = await fetch('/pause');
        } else {
            const response = await fetch('/resume');
        }
    }

    async function skipSong() {
        await fetch('/skip');
    }

    return (
        <>
            <Center>
                <Button onClick={toggleColorMode}>
                    <FaLightbulb /> {colorMode === 'light' ? '' : ''}
                </Button>
                <Box paddingRight={10} paddingLeft={10}>
                    <Button onClick={handleClick}>
                        {buttonState === "play" ? (
                            <Icon as={FaPlay} />
                        ) : (
                            <Icon as={FaPause} />
                        )}
                    </Button>
                </Box>
                <Button onClick={skipSong}>
                    <Icon as={FaStepForward} />
                </Button>
            </Center>
						<Center>
            <Input marginTop={10} width="80%"
              placeholder="Search for music via query or url" 
							onKeyPress={handleKeyPress} onKeyUpCaptur 
							value={value}
							onChange={handleChange}
						/>
						</Center>
        </>
    );
}

export default PlayControls;