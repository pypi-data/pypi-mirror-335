from ..enums import SlotInteractionType
from ..generic import GamePacket


class DropItemPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.items.DropItemPacket"

    window_id: int
    item_slot_num: int
    desired_amount: int


class SlotInteractPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.items.SlotInteractPacket"

    interaction_type: SlotInteractionType
    window_id: int
    slot_id: int


class ContainerSyncPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.items.ContainerSyncPacket"
    )

    window_id: int
    # TODO


class RequestGiveItemPacket(GamePacket):
    PACKET_NAME = (
        "finalforeach.cosmicreach.networking.packets.items.RequestGiveItemPacket"
    )

    window_id: int
    # TODO
    slot_num: int


class SlotSyncPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.items.SlotSyncPacket"

    window_id: int
    # TODO


class SlotSwapPacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.items.SlotSwapPacket"

    window_id_src: int
    slot_id_src: int
    window_id_dst: int
    slot_id_dst: int


class SlotMergePacket(GamePacket):
    PACKET_NAME = "finalforeach.cosmicreach.networking.packets.items.SlotMergePacket"

    window_id_src: int
    window_id_dst: int
    slot_id_src: int
