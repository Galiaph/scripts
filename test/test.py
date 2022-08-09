__author__ = "Vadim Shemyatin"

"""
Скрипт для генерации профилей BDCOM
"""

with open("test.txt", "w") as f:
    for i in range(1, 9):
        for j in range(1, 65):
            f.write("!\n")
            f.write("epon onu-config-template EPON0/{}:{}\n".format(i, j))
            f.write(" cmd-sequence 1 epon onu all-port ctc vlan mode tag {}{:02d}\n".format(i, j))
            f.write(" cmd-sequence 2 epon sla upstream pir 1000000 cir 10000\n")
            f.write(" cmd-sequence 3 epon sla downstream pir 1000000 cir 10000\n")
            # f.write(" cmd-sequence 4 epon onu all-port loopback detect\n")
            f.write(" cmd-sequence 4 epon fec enable\n")


"""
Скрипт для генерации профилей C-DATA
"""
# profCount = 1

# with open("test.txt", "w") as f:
#     for i in range(1, 9):
#         for j in range(1, 65):
#             f.write("ont-srvprofile epon profile-id {} profile-name epon0/{}:{}\n".format(profCount, i, j))
#             f.write("  ont-port eth 1 pots 0 catv 0\n")
#             f.write("  port eth 1 up-policing 1 ds-policing 1\n")
#             f.write("  port vlan eth 1 translation {}{:02d} user-vlan {}{:02d} 0\n".format(i, j, i, j))
#             f.write("  port native-vlan eth 1 {}{:02d}\n".format(i, j))
#             f.write("  commit\n")
#             f.write(" exit\n")
#             f.write("!\n")
#             profCount += 1
#     profCount = 1
#     for i in range(1, 9):
#         for j in range(1, 65):
#             f.write("  ont predetermine {} {} ont-lineprofile-id 0 ont-srvprofile-id {}\n".format(i, j, profCount))
#             profCount += 1

"""
Скрипт для поиска совподений в профилях
"""

# with open("st.txt", "r") as f:
#     str = f.readlines()
#     list_match = list()

#     for i in range(1, 9):
#         for j in range(1, 65):
#             match = f"epon onu-config-template EPON0/{i}:{j}\n"
#             if (match not in str):
#                 list_match.append(match)

#     print(len(list_match))

# for i in range(1, 49):
#     print("vlan 1{:02}".format(i))
#     print("   name \"VLAN1{:02}\"".format(i))
#     print("   untagged {}".format(i))
#     print("   tagged 49-52")
#     print("   exit")
