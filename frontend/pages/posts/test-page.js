import { DragDropContext, Draggable, Droppable } from "react-beautiful-dnd";
import { Flex, Image, Text, Spinner, Center, Box } from "@chakra-ui/react";

const items = [
  {
    id: "item-1",
    content: "Item 1",
  },
  {
    id: "item-2",
    content: "Item 2",
  },
  {
    id: "item-3",
    content: "Item 3",
  },
];

function TestPage() {
  const onDragEnd = (result) => {};
  return (
    <>
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="items">
          {(provided, snapshot) => (
            <Flex ref={provided.innerRef} {...provided.droppableProps}>
              {items.map((item, index) => (
                <Draggable key={item.id} draggableId={item.id} index={index}>
                  {(provided, snapshot) => (
                    <Box
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                    >
                      {item.content}
                    </Box>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </Flex>
          )}
        </Droppable>
      </DragDropContext>
    </>
  );
}

export default TestPage;