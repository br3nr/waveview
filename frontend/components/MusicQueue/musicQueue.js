import React, { useState, useCallback } from "react";
import { Flex, Image, Text, Spinner, Box } from "@chakra-ui/react";
import { IconButton } from "@chakra-ui/react";
import { RxCross2 } from "react-icons/rx";
import styles from "./musicQueue.module.css";
import QueueChip from "./QueueChip/queueChip";
import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";

function MusicQueue(props) {
  const [removedTrackIds, setRemovedTrackIds] = useState([]);

  const removeTrack = useCallback(
    async (track) => {
      setRemovedTrackIds([...removedTrackIds, track.uuid]);
      const url = `/remove_track/${localStorage.getItem("serverId")}/${
        track.uuid
      }`;
      await fetch(url);
    },
    [removedTrackIds]
  );

  const onDragEnd = async (result) => {
    if (!result.destination) {
      return;
    }
    const items = Array.from(props.trackQueue);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    props.setTrackQueue(items);
    const reorderedItemUuid = reorderedItem.uuid;
    const url = `/reorder/${localStorage.getItem("serverId")}/${reorderedItemUuid}/${
      result.destination.index}`;
    await fetch(url);
  };

  return (
    <>
      <Flex
        flexDirection="column"
        overflowY="scroll"
        width="100%"
        height="800px"
        marginTop="10px"
        className={styles.customScrollbar}
      >
        <DragDropContext onDragEnd={onDragEnd}>
          <Droppable droppableId="items">
            {(provided, snapshot) => (
              <Box ref={provided.innerRef} {...provided.droppableProps}>
                {props.trackQueue.map((track, index) => (
                  <Draggable
                    key={track.id.toString()}
                    draggableId={track.id.toString()}
                    index={index}
                    
                  >
                    {(provided, snapshot) => (
                      <Box
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        style={{
                          userSelect: "none",
                          padding:"6px",
                          margin: "0 0 4px 4px",
                          minHeight: "50px",
                          borderRadius: "1px",
                         
                          ...provided.draggableProps.style,
                        }}
                      >
                        <QueueChip
                          track={track}
                          removedTrackIds={removedTrackIds}
                          removeTrack={removeTrack}
                        ></QueueChip>
                      </Box>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </Box>
            )}
          </Droppable>
        </DragDropContext>
      </Flex>
    </>
  );
}

export default MusicQueue;
