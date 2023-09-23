import cv2
import mido

# Connect to the MIDI device
try:
    inport = mido.open_input()
except OSError:
    inport = None

# Get the Default resolutions
cap = cv2.VideoCapture(0)
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# Define the codec and filename.
out = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))

# Define keyboard parameters
white_key_height = 150
black_key_height = 75
octaves = 7  # Number of octaves to display
white_key_width = frame_width // 52  # 52 white keys in total
black_key_width = white_key_width // 2

# Define colors (BGR)
white = (255, 255, 255)
black = (0, 0, 0)
blue = (255, 0, 0)  # Key will turn blue when pressed
gray = (125, 125, 125)  # For bevel
green = (0, 255, 0)  # Key will turn green when pressed

# Create a state for each key on the keyboard
midi_state = [0] * 128

# This will map Midi Notes to the notes on the keyboard.
white_notes_mapper = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108, 110, 112, 113, 115, 117, 119, 120, 122, 124, 125]
black_notes_mapper = [1, 3, 6, 8, 10, 13, 15, 18, 20, 22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106, 109, 111, 114, 116, 118, 121, 123, 126]

while cap.isOpened():
    if (inport):
        for msg in inport.iter_pending():
            if msg.type == 'note_on' and msg.velocity > 0:
                midi_state[msg.note] = 1
            elif msg.type == 'note_on' and msg.velocity == 0:  # Some controllers send an 0 velocity with "note_on" to indicate note is off.
                midi_state[msg.note] = 0
            elif msg.type == 'note_off':
                midi_state[msg.note] = 0

    ret, frame = cap.read()
    if ret:
        # Draw white keys
        for i in range(74):
            top_left = (i * white_key_width, frame_height - white_key_height)
            bottom_right = ((i + 1) * white_key_width, frame_height)
            midi_note = white_notes_mapper[i]

            if (midi_state[midi_note]):
                color = green
            else:
                color = white
         
            cv2.rectangle(frame, top_left, bottom_right, color, -1)
            cv2.line(frame, top_left, (top_left[0], bottom_right[1]), gray, 2)  # Left bevel
            cv2.line(frame, top_left, (bottom_right[0], top_left[1]), gray, 2)  # Top bevel

        # Draw black keys
        # The pattern of black keys within an octave (1 means a black key is present)
        black_key_pattern = [1, 1, 0, 1, 1, 1, 0]
        black_note_counter = 0
        for i in range(52):  # There are 52 black keys in total
            # Calculate the octave and the note within the octave (from 0 to 6)
            octave, note_in_octave = divmod(i, 7)

            # Skip the iteration if there's no black key at the current note
            if black_key_pattern[note_in_octave] == 0:
                continue

            # Calculate the position of the white key that's to the left of the black key
            white_key_index = octave * 7 + note_in_octave + 1  # We start from the second white key

            top_left = (int(white_key_index * white_key_width - black_key_width/2), frame_height - 150)
            bottom_right = (int(white_key_index * white_key_width + black_key_width/2), frame_height - 70)

            midi_note = black_notes_mapper[black_note_counter]

            if (midi_state[midi_note]):
                color = green
            else:
                color = black

            cv2.rectangle(frame, top_left, bottom_right, color, -1)

            black_note_counter += 1

        # Write the frame
        out.write(frame)

        # Show the frame
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()