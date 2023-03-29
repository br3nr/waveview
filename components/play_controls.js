import { Box, Center, Button, Icon, useColorMode } from "@chakra-ui/react";
import { FaPlay, FaPause, FaStepForward, FaLightbulb } from "react-icons/fa";
import React from "react";
import { useState } from "react";
import { Input, Form } from "@chakra-ui/react";

function PlayControls(props) {
	const [buttonState, setButtonState] = useState("pause");
	const [spinning, setSpinning] = useState(0);
	const [value, setValue] = React.useState('')
	const handleChange = (event) => setValue(event.target.value)

	const handleKeyPress = async (event) => {
		if (event.key === "Enter") {
			setValue("")
			const url = `/play_song/${props.selectedServer.id}/${value}`;
			await fetch(url);
			// Do something, e.g. submit a query
			console.log("Enter key pressed!");
			console.log(value)
		}
	};

	async function handleClick() {
		setButtonState(buttonState === "play" ? "pause" : "play");

		if (buttonState == "pause") {
			const response = await fetch(`/pause/${props.selectedServer.id}`);
		} else {
			const response = await fetch(`/resume/${props.selectedServer.id}`);
		}
	}

	async function skipSong() {
		await fetch(`/skip/${props.selectedServer.id}`);
	}

	return (
		<>
			<Center>
				<Box paddingRight={10} >
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
					onKeyPress={handleKeyPress}
					value={value}
					onChange={handleChange}
				/>
			</Center>
		</>
	);
}

export default PlayControls;