import React, { useState, useEffect, useCallback } from 'react';
import { Button, Flex, Image, Text, Spinner, Box } from '@chakra-ui/react';
import { MdPlaylistRemove } from 'react-icons/md';

function MusicQueue(props) {
	const [removedTrackIds, setRemovedTrackIds] = useState([]);

	function setTrackQueue(track) {
		props.setTrackQueue(track);
	}

	const removeTrack = useCallback(async (track) => {
		setRemovedTrackIds([...removedTrackIds, track.uuid]);
		const url = `/remove_track/${props.selectedServer}/${track.uuid}`;
		await fetch(url);
	}, [removedTrackIds]);

	useEffect(() => {
		const newQueue = props.trackQueue.filter((t) => !removedTrackIds.includes(t.uuid));
		setTrackQueue(newQueue);
	}, [props.trackQueue, removedTrackIds]);

	return (
		<>
			<Flex flexDirection="column" overflowY="scroll" height="800px" marginTop="10px">
				{props.trackQueue.map((track) => (
					<Flex key={track.id} borderRadius="50px" alignItems="center" width={550} margin="10px" >
						<Flex w="80%" alignItems="center">
							<Image
								src={track.thumbnail}
								alt={track.title}
								boxSize="50px"
								objectFit="cover"
								borderRadius="10px"
							/>
							<Text
								marginLeft="15px"
								marginRight="0px"
								as='h2'
								size='md'
								noOfLines={1}
							>
								{track.title}
							</Text>
						</Flex>
						<Flex w="20%">
							<Button
								height="50px"
								borderRadius="50px"
								background="transparent"
								onClick={() => removeTrack(track)} marginLeft="auto">
								{removedTrackIds.includes(track.uuid) ? (
									<Spinner size='xs' />
								) : (
									<MdPlaylistRemove />
								)}
							</Button>
						</Flex>
					</Flex>
				))}
			</Flex>
		</>
	)
}


export default MusicQueue;